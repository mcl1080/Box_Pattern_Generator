def convert_to_mm(value, unit):
    """
    Convert a measurement to millimeters from various units.

    Args:
        value (float): The measurement value
        unit (str): The unit ('mm', 'cm', 'in')

    Returns:
        float: The value converted to millimeters
    """
    unit = unit.lower()
    if unit == 'mm':
        return value
    elif unit == 'cm':
        return value * 10.0
    elif unit == 'in':
        return value * 25.4
    else:
        raise ValueError(f"Unsupported unit: {unit}")


def parse_dimension(dimension_str):
    """
    Parse a dimension string into a value and unit.

    Args:
        dimension_str (str): A string like '10mm', '2.5cm', '1in', or just '10'

    Returns:
        tuple: (value in mm, original unit)
    """
    dimension_str = dimension_str.strip()

    # Regular expression to find a number followed by optional units
    import re
    match = re.match(r'([\d.]+)(\s*)([a-zA-Z]*)', dimension_str)

    if not match:
        raise ValueError(f"Invalid dimension format: {dimension_str}")

    value = float(match.group(1))
    unit = match.group(3).lower() or 'mm'  # Default to mm if no unit given

    # Normalize unit
    if unit in ['millimeter', 'millimeters', 'mm']:
        unit = 'mm'
    elif unit in ['centimeter', 'centimeters', 'cm']:
        unit = 'cm'
    elif unit in ['inch', 'inches', 'in']:
        unit = 'in'

    return convert_to_mm(value, unit), unit  # !/usr/bin/env python3


import math
from collections import defaultdict


class LineSegment:
    def __init__(self, x1, y1, x2, y2):
        # A tiny tolerance for floating point comparison
        self.tolerance = 1e-6

        # Check if this is a horizontal or vertical line
        self.is_horizontal = abs(y1 - y2) < self.tolerance
        self.is_vertical = abs(x1 - x2) < self.tolerance

        # Ensure the line segment is always oriented from left to right
        # or top to bottom to simplify comparison
        if ((self.is_horizontal and x1 > x2) or
                (self.is_vertical and y1 > y2) or
                (not self.is_horizontal and not self.is_vertical and x1 > x2)):
            self.x1, self.y1 = x2, y2
            self.x2, self.y2 = x1, y1
        else:
            self.x1, self.y1 = x1, y1
            self.x2, self.y2 = x2, y2

    def get_overlap(self, other):
        """Returns the overlapping portion of two line segments, or None if they don't overlap."""
        if not self.is_parallel_to(other):
            return None

        # For horizontal lines
        if self.is_horizontal and other.is_horizontal and abs(self.y1 - other.y1) < self.tolerance:
            # Find overlapping x range
            min_x = max(self.x1, other.x1)
            max_x = min(self.x2, other.x2)

            if max_x - min_x >= -self.tolerance:  # Allow tiny negative for floating point errors
                return LineSegment(min_x, self.y1, max_x, self.y1)
            return None

        # For vertical lines
        elif self.is_vertical and other.is_vertical and abs(self.x1 - other.x1) < self.tolerance:
            # Find overlapping y range
            min_y = max(self.y1, other.y1)
            max_y = min(self.y2, other.y2)

            if max_y - min_y >= -self.tolerance:  # Allow tiny negative for floating point errors
                return LineSegment(self.x1, min_y, self.x1, max_y)
            return None

        return None

    def is_parallel_to(self, other):
        """Check if this line is parallel to another line."""
        if (self.is_horizontal and other.is_horizontal) or (self.is_vertical and other.is_vertical):
            return True
        # For diagonal lines, check if slopes are the same
        if not self.is_horizontal and not self.is_vertical and not other.is_horizontal and not other.is_vertical:
            # Calculate slopes
            self_slope = (self.y2 - self.y1) / (self.x2 - self.x1) if self.x2 != self.x1 else float('inf')
            other_slope = (other.y2 - other.y1) / (other.x2 - other.x1) if other.x2 != other.x1 else float('inf')
            return abs(self_slope - other_slope) < self.tolerance
        return False

    def subtract(self, overlapping_segment):
        """Returns the non-overlapping portions of this line after removing an overlapping segment."""
        results = []

        # For horizontal lines
        if self.is_horizontal:
            # Left segment (if exists)
            if overlapping_segment.x1 > self.x1 + self.tolerance:
                results.append(LineSegment(self.x1, self.y1, overlapping_segment.x1, self.y1))

            # Right segment (if exists)
            if overlapping_segment.x2 < self.x2 - self.tolerance:
                results.append(LineSegment(overlapping_segment.x2, self.y1, self.x2, self.y1))

        # For vertical lines
        elif self.is_vertical:
            # Top segment (if exists)
            if overlapping_segment.y1 > self.y1 + self.tolerance:
                results.append(LineSegment(self.x1, self.y1, self.x1, overlapping_segment.y1))

            # Bottom segment (if exists)
            if overlapping_segment.y2 < self.y2 - self.tolerance:
                results.append(LineSegment(self.x1, overlapping_segment.y2, self.x1, self.y2))

        return results

    def length(self):
        """Calculate the length of the line segment."""
        return math.sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

    def to_svg(self, color="black", width=0.5):
        """Convert to SVG line element."""
        return f'<line x1="{self.x1}" y1="{self.y1}" x2="{self.x2}" y2="{self.y2}" stroke="{color}" stroke-width="{width}" />'

    def __eq__(self, other):
        """Check if two line segments are exactly the same."""
        return (abs(self.x1 - other.x1) < self.tolerance and
                abs(self.y1 - other.y1) < self.tolerance and
                abs(self.x2 - other.x2) < self.tolerance and
                abs(self.y2 - other.y2) < self.tolerance)

    def __hash__(self):
        """Hash for dictionary keys."""
        return hash((round(self.x1, 6), round(self.y1, 6),
                     round(self.x2, 6), round(self.y2, 6)))

    def __repr__(self):
        """String representation for debugging."""
        return f"Line({self.x1},{self.y1} -> {self.x2},{self.y2})"


def extract_rectangle_lines(x, y, width, height):
    """Extract the four line segments that make up a rectangle."""
    return [
        LineSegment(x, y, x + width, y),  # Top
        LineSegment(x + width, y, x + width, y + height),  # Right
        LineSegment(x, y + height, x + width, y + height),  # Bottom
        LineSegment(x, y, x, y + height)  # Left
    ]


def extract_polygon_lines(points_str):
    """Extract line segments from a polygon points string."""
    # Parse the points string into coordinates
    points = []
    for point in points_str.strip().split():
        if ',' in point:
            x, y = point.split(',')
            points.append((float(x), float(y)))

    # Create line segments between consecutive points
    lines = []
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]  # Wrap around to the first point
        lines.append(LineSegment(x1, y1, x2, y2))

    return lines


def find_overlapping_segments(all_lines):
    """Find all overlapping and non-overlapping line segments."""
    # Group lines for overlap detection
    horizontal_lines = defaultdict(list)
    vertical_lines = defaultdict(list)
    diagonal_lines = []

    # First, categorize all lines
    for line in all_lines:
        if line.is_horizontal:
            # Group by y-coordinate
            y_key = round(line.y1, 6)
            horizontal_lines[y_key].append(line)
        elif line.is_vertical:
            # Group by x-coordinate
            x_key = round(line.x1, 6)
            vertical_lines[x_key].append(line)
        else:
            diagonal_lines.append(line)

    # Lists to store results
    unique_segments = []  # Non-overlapping segments (black)
    overlap_segments = []  # Overlapping segments (green)

    # Helper to check if a segment overlaps with any in the overlap list
    def is_duplicate_overlap(test_segment):
        for existing_overlap in overlap_segments:
            if (abs(test_segment.x1 - existing_overlap.x1) < test_segment.tolerance and
                    abs(test_segment.y1 - existing_overlap.y1) < test_segment.tolerance and
                    abs(test_segment.x2 - existing_overlap.x2) < test_segment.tolerance and
                    abs(test_segment.y2 - existing_overlap.y2) < test_segment.tolerance):
                return True
        return False

    # Process horizontal lines
    for y_coord, lines in horizontal_lines.items():
        # Sort lines by x1 coordinate
        lines.sort(key=lambda l: l.x1)

        # Find all overlaps
        segments_to_process = lines.copy()
        processed_segments = []

        while segments_to_process:
            current = segments_to_process.pop(0)
            found_overlap = False

            # Check for overlaps with all other unprocessed lines
            for other in segments_to_process[:]:
                overlap_segment = current.get_overlap(other)
                if overlap_segment and overlap_segment.length() > 0.1:  # Ensure significant overlap
                    found_overlap = True

                    # Add the overlap to the overlaps list if it's not already there
                    if not is_duplicate_overlap(overlap_segment):
                        overlap_segments.append(overlap_segment)

                    # Handle the current line's non-overlapping parts
                    non_overlapping = current.subtract(overlap_segment)
                    segments_to_process.extend(non_overlapping)

                    # Handle the other line's non-overlapping parts
                    non_overlapping_other = other.subtract(overlap_segment)
                    segments_to_process.remove(other)
                    segments_to_process.extend(non_overlapping_other)

                    # Skip further processing of the current line
                    break

            # If no overlaps found, this is a unique segment
            if not found_overlap:
                processed_segments.append(current)

        # Add all processed segments that have no overlaps
        unique_segments.extend(processed_segments)

    # Process vertical lines (similar logic)
    for x_coord, lines in vertical_lines.items():
        # Sort lines by y1 coordinate
        lines.sort(key=lambda l: l.y1)

        # Find all overlaps
        segments_to_process = lines.copy()
        processed_segments = []

        while segments_to_process:
            current = segments_to_process.pop(0)
            found_overlap = False

            # Check for overlaps with all other unprocessed lines
            for other in segments_to_process[:]:
                overlap_segment = current.get_overlap(other)
                if overlap_segment and overlap_segment.length() > 0.1:  # Ensure significant overlap
                    found_overlap = True

                    # Add the overlap to the overlaps list if it's not already there
                    if not is_duplicate_overlap(overlap_segment):
                        overlap_segments.append(overlap_segment)

                    # Handle the current line's non-overlapping parts
                    non_overlapping = current.subtract(overlap_segment)
                    segments_to_process.extend(non_overlapping)

                    # Handle the other line's non-overlapping parts
                    non_overlapping_other = other.subtract(overlap_segment)
                    segments_to_process.remove(other)
                    segments_to_process.extend(non_overlapping_other)

                    # Skip further processing of the current line
                    break

            # If no overlaps found, this is a unique segment
            if not found_overlap:
                processed_segments.append(current)

        # Add all processed segments that have no overlaps
        unique_segments.extend(processed_segments)

    # Add diagonal lines (since they're less likely to overlap)
    unique_segments.extend(diagonal_lines)

    # Final cleanup: Ensure no segment appears in both lists
    # and filter out very short segments
    min_length = 0.1  # Minimum length to keep

    # Filter unique segments
    filtered_unique = []
    for segment in unique_segments:
        if segment.length() > min_length and not is_duplicate_overlap(segment):
            filtered_unique.append(segment)

    # Filter overlap segments
    filtered_overlap = []
    for segment in overlap_segments:
        if segment.length() > min_length:
            # Check for duplicates in the overlap list itself
            is_duplicate = False
            for existing in filtered_overlap:
                if (abs(segment.x1 - existing.x1) < segment.tolerance and
                        abs(segment.y1 - existing.y1) < segment.tolerance and
                        abs(segment.x2 - existing.x2) < segment.tolerance and
                        abs(segment.y2 - existing.y2) < segment.tolerance):
                    is_duplicate = True
                    break
            if not is_duplicate:
                filtered_overlap.append(segment)

    return filtered_unique, filtered_overlap


def create_connected_rectangles_svg(width, length, height, material_thickness=3, flap_length=15,
                                    filename="connected_rectangles.svg"):
    """
    Creates an SVG file with 4 rectangles connected left to right, plus additional
    rectangles above and below each one. Also adds a tapered shape to the left.

    Args:
        width (float): Internal width dimension in millimeters
        length (float): Internal length dimension in millimeters
        height (float): Internal height dimension in millimeters (used for the middle row)
        material_thickness (float): Material thickness in millimeters
        flap_length (float): Length of the tapered flap in millimeters
        filename (str): Output filename for the SVG file
    """
    # Adjust dimensions to account for material thickness
    # For internal dimensions to match input, we need to add material thickness to external dimensions
    adjusted_width = width + material_thickness
    adjusted_length = length + material_thickness
    adjusted_height = height + material_thickness

    # Calculate the height for the top and bottom rectangles
    small_height = min(adjusted_width, adjusted_length, adjusted_height) / 2

    # Calculate inset amount for top and bottom rectangles (half of material thickness)
    inset = material_thickness / 2

    # Tapered shape dimensions
    taper_width = flap_length  # Use the flap_length parameter (default is 15mm)
    taper_angle = 30  # degrees

    # Calculate the height difference for the taper (both top and bottom)
    taper_height_diff = taper_width * math.tan(math.radians(taper_angle))

    # Calculate total width and height of the SVG
    total_width = 2 * adjusted_width + 2 * adjusted_length + taper_width
    total_height = adjusted_height + 2 * small_height + 2 * material_thickness  # Increased for the shifted rectangles

    # Define the column widths and positions
    column_widths = [adjusted_width, adjusted_length, adjusted_width, adjusted_length]

    # Define line segments for all shapes
    all_lines = []

    # Line segments for the tapered shape
    tapered_y_top = small_height  # Same y as middle row
    half_taper = taper_height_diff / 2  # Half the taper amount for top and bottom

    # Extract points for the tapered shape polygon
    tapered_points = f"""
    0,{tapered_y_top + half_taper}
    {taper_width},{tapered_y_top}
    {taper_width},{tapered_y_top + adjusted_height}
    0,{tapered_y_top + adjusted_height - half_taper}
    """
    all_lines.extend(extract_polygon_lines(tapered_points))

    # Start x position after the tapered shape
    x_pos = taper_width

    # Define the y-positions for each row
    y_top = 0  # Top row
    y_middle = small_height  # Middle row
    y_bottom = small_height + adjusted_height  # Bottom row

    # Extract line segments for all rectangles
    for i, column_width in enumerate(column_widths):
        # For the second and fourth rectangles in the middle row (length rectangles),
        # extend their height by material_thickness at top and bottom and adjust top/bottom rectangles
        if i == 1 or i == 3:  # Second or fourth rectangle (length rectangles)
            # Top rectangle - narrower by inset on each side and moved up by material_thickness
            all_lines.extend(extract_rectangle_lines(
                x_pos + inset, y_top - material_thickness, column_width - 2 * inset, small_height
            ))

            # Middle rectangle - extended by material_thickness at top and bottom
            all_lines.extend(extract_rectangle_lines(
                x_pos, y_middle - material_thickness, column_width, adjusted_height + 2 * material_thickness
            ))

            # Bottom rectangle - narrower by inset on each side and moved down by material_thickness
            all_lines.extend(extract_rectangle_lines(
                x_pos + inset, y_bottom + material_thickness, column_width - 2 * inset, small_height
            ))
        else:  # First and third rectangle (width rectangles)
            # Top rectangle - narrower by inset on each side
            all_lines.extend(extract_rectangle_lines(
                x_pos + inset, y_top, column_width - 2 * inset, small_height
            ))

            # Middle rectangle - normal height
            all_lines.extend(extract_rectangle_lines(
                x_pos, y_middle, column_width, adjusted_height
            ))

            # Bottom rectangle - narrower by inset on each side
            all_lines.extend(extract_rectangle_lines(
                x_pos + inset, y_bottom, column_width - 2 * inset, small_height
            ))

        # Update x position for next column
        x_pos += column_width

    # Find overlapping and non-overlapping segments
    unique_segments, overlap_segments = find_overlapping_segments(all_lines)

    # Create SVG with line highlighting
    svg_header = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="{total_width}mm" height="{total_height}mm" viewBox="0 0 {total_width} {total_height}"
     xmlns="http://www.w3.org/2000/svg" version="1.1">'''

    # Create SVG elements
    svg_elements = []

    # Create a single path for all black (non-overlapping) lines
    if unique_segments:
        path_data = []
        for line in unique_segments:
            path_data.append(f"M {line.x1},{line.y1} L {line.x2},{line.y2}")

        # Join all path data into a single path element
        svg_elements.append(f'  <path d="{" ".join(path_data)}" fill="none" stroke="black" stroke-width="0.5"/>')

    # Keep green (overlapping) lines as individual line elements
    for line in overlap_segments:
        svg_elements.append("  " + line.to_svg("green", 1.0))

    # SVG footer
    svg_footer = '</svg>'

    # Combine all parts
    svg_content = svg_header + '\n' + '\n'.join(svg_elements) + '\n' + svg_footer

    # Write the SVG content to a file
    with open(filename, 'w') as f:
        f.write(svg_content)

    print(f"SVG file '{filename}' has been created successfully.")
    print(f"Total dimensions: {total_width}mm × {total_height}mm")


def main():
    print("Box SVG Generator")
    print("============================================================")
    print("Note: Enter the INTERNAL dimensions of your desired box")
    print("You can use 'mm', 'cm', or 'in' units (default is mm if no unit specified)")
    print("------------------------------------------------------------")

    try:
        # Prompt user for all dimensions
        dim1_input = input("Enter first dimension (e.g., 50mm, 5cm, 2in): ")
        dim2_input = input("Enter second dimension: ")
        dim3_input = input("Enter third dimension: ")

        # Parse dimensions and convert to mm
        dim1_mm, dim1_unit = parse_dimension(dim1_input)
        dim2_mm, dim2_unit = parse_dimension(dim2_input)
        dim3_mm, dim3_unit = parse_dimension(dim3_input)

        # Sort dimensions to determine width (smallest), length (middle), and height (largest)
        dimensions = sorted([dim1_mm, dim2_mm, dim3_mm])
        width, length, height = dimensions

        print(f"\nBox dimensions (internal):")
        print(f"  Width: {width:.1f}mm")
        print(f"  Length: {length:.1f}mm")
        print(f"  Height: {height:.1f}mm")

        # Prompt for material thickness with default value
        material_input = input("\nEnter material thickness (default: 3mm): ")
        try:
            if material_input.strip():
                material_thickness, _ = parse_dimension(material_input)
            else:
                material_thickness = 3.0
            print(f"Material thickness: {material_thickness:.1f}mm")
        except ValueError:
            print("Invalid format. Using default 3mm thickness.")
            material_thickness = 3.0

        # Prompt for flap length with default value
        flap_input = input("\nEnter flap length (default: 15mm): ")
        try:
            if flap_input.strip():
                flap_length, _ = parse_dimension(flap_input)
            else:
                flap_length = 15.0
            print(f"Flap length: {flap_length:.1f}mm")
        except ValueError:
            print("Invalid format. Using default 15mm flap length.")
            flap_length = 15.0

        # Optional filename input
        default_filename = "box.svg"
        filename_input = input(f"\nEnter filename (default: {default_filename}): ")
        filename = filename_input if filename_input.strip() else default_filename

        # Add .svg extension if not provided
        if not filename.lower().endswith('.svg'):
            filename += '.svg'

        # Create the SVG file
        create_connected_rectangles_svg(width, length, height, material_thickness, flap_length, filename)

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()