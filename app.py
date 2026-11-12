
from server import create_app

app = create_app()


@app.route("/")
def home():
    return {
        "message": "Welcome to FoundIt API!",
        "status": "Backend is running successfully"
    }


if __name__ == "__main__":
    app.run(debug=True, port=5555)
