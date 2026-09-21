def optimize_page_memory(page):
    """
    Blocks heavy resources from loading to prevent RAM crashes on Streamlit Cloud.
    """
    def intercept_route(route):
        if route.request.resource_type in ["image", "media", "font"]:
            route.abort()
        else:
            route.continue_()

    page.route("**/*", intercept_route)