from webui.app import create_app

# Create the Flask web application by calling the create_app function
app = create_app()

# Run the app on port 5000 and enable debug mode
if __name__ == "__main__":
    app.run(port=5000, debug=True)