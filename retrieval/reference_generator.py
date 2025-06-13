def format_references(kb_results: list, web_results: list) -> str:
    """
    Add references to response
    """
    references = []
    
    # YouTube references
    if kb_results:
        references.append("\n\n**Reference Videos:**")
        for content, video_id, start_time, similarity in kb_results:
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            references.append(
                f"- [{video_id} ({minutes}:{seconds:02d})](https://youtu.be/{video_id}?t={int(start_time)})"
            )
    
    # web references
    if web_results:
        references.append("\n\n**Web References:**")
        for result in web_results:
            references.append(f"- [{result['title']}]({result['url']})")
    
    return "\n".join(references) if references else ""