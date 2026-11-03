# mp2-data-processing-API


echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".pytest_cache/" >> .gitignore

If you upload a CSV, store it in memory, clean it up, and pull the rows back out over HTTP, it can give the following endpoints: “GET/health” returns the app status and version; “POST /upload” takes a CSV, stores it, and returns its ID, filename, row/column counts, and column names; “GET /datasets/{dataset_id}” returns up to limit rows plus the total row count; “POST /datasets/{dataset_id}/process” validates and cleans a stored dataset using MP1 modules to return a cleaning report. To do this project I first built up the API foundation, as part of mp2-part1. Then I brought in my MP1 code and completed connecting and processing the API, as part of mp2-part2. I had to do a lot of debugging and it was focused around fixing my imported MP1 files as I wasn’t able to finish it and had to do them now to import it along with repositioning the files into the correct location without being nested, cleaning up the processing endpoint as there were some variations in the code, and other mini clean-ups in terms of improper naming, cleaning up formatting and spacing.

