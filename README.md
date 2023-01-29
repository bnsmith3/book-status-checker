# book-status-checker

The code herein creates a simple Flask app that helps me to easily track books that I have read and to query the [Fairfax County Public Library system](https://www.fairfaxcounty.gov/library/) for the avavilability of books that I would like to check out in the future.

This was initially created to better understand how Flask works as most of my prior experience accomplishing comparable simple tasks utilized Django.

## Usage

To run the **book-status-checker** app using the built-in server in development mode on Windows, navigate into the `status_checker` folder and execute the following statements:
```
set FLASK_APP=status_checker.py
set FLASK_ENV=development
flask run
```

If you would like to run the server in regular mode, do not set the Flask environment variable to "development".

After the commands are run, the Flask app can then be accessed via any browser by navigating to http://127.0.0.1:5000/.

The package versions utilized during the creation of this code can be found in the [`environment.yml`](./environment.yml) file.
