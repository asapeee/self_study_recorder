from apps.app import create_app


app = create_app('local')
app.run(debug=True, host='0.0.0.0')