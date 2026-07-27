class StudentListResponse(BaseModel):
    items: list[StudentRead]
    total_items: int
    page: int
    page_size: int