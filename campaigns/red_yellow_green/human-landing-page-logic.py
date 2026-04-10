# 🧠 9. Example Human Landing Page Logic
# You can route based on validation state:
@app.get("/")
async def landing_page(request: Request):
    state = determine_validation_state()  # red, yellow, green, default

    page_map = {
        "red": "human/red-light.html",
        "yellow": "human/yellow-light.html",
        "green": "human/green-light.html",
        "default": "human/default-landing-page.html"
    }

    return HTMLResponse(open(page_map[state]).read())
