
def sort_and_slice_reports(reports, limit=25, offset=0):
    """
    Sorts reports by submitted_at (descending) and returns a slice.
    """
    # Sort by submitted_at descending

    sorted_reports = sorted(reports, key=lambda x: x.get('submitted_at', ''), reverse=True)
    
    # Slice
    return sorted_reports[offset : offset + limit]
