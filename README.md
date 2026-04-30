# python-backend-locations
Backend FastAPI server supporting CRUD operations for android location logger app data

Location schema:
    latitude
    logitude
    time
    id
    source
    


To run the app: 
    pipenv shell
    fastapi dev main.py
        OR
    pipenv run uvicorn main:app --reload

To run tests: 
    pipenv run python -m pytest tests/test_main.py -v
