start:
	cd kth_qa && uvicorn main:app --host localhost --port 5001 --reload

ingest:
	cd kth_qa && python3 ingest.py

courses:
	python webscraping/scrape_course.py

course_info:
	python webscraping/scrape_info.py