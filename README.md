Fyyur
-----

## Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

While the views and controlled had been defined for me in this application, models and model interactions were missing. My job is to build out the data models to power the API endpoints for the Fyyur site by connecting to a PostgreSQL database for creating, storing, retrieving, updating and even deleting information about artists and venues on Fyyur.

The booking site has the following functionality:

* creating new venues, artists, and new shows.
* knowing more about a specific artist or venue.
* searching for venues and artists.
* updating the details of a specific artist or venue.
* deleting the information of a specific artist or venue.

## Tech Stack

Highlight folders:
* `templates/pages` -- Defines the pages that are rendered to the site. These templates render views based on data passed into the template’s view, in the controllers defined in `app.py`. These pages successfully represent the data to the user.
* `templates/layouts` -- Defines the layout that a page can be contained in to define footer and header code for a given page.
* `templates/forms` -- Defines the forms used to create new artists, shows, and venues.
* `app.py` -- Defines routes that match the user’s URL, and controllers that handle data and renders views to the user by manipulating the database.
* `models.py` -- Defines the data models that set up the database tables, and connect the app and the database.
* `config.py` -- Stores configuration variables and instructions, separate from the main application code. 

Development Techniques Used:
1. Set up normalzied models using SQLAlchemy. Best practices in database scheme design are followed to implement model properties and relationships.
2. Maintained version control of the databases using database migrations via Flask-Migrate.
3. Created form submissions for entering new venues, artists and shows to insert proper new records in the database. There are propoer constaints enacted that powers the `/create` endpoints that serve the form templates, to prevent duplicate and nonsensical form submissions.
4. Implemented the controllfers for listing venues, artists and shows.
5. Enabled the `/search` endpoints that power the application's search functionalities.
6. Wrote the `<venue|artist>/<id>` endpoints that serve the venue and artist detail pages

## Setup and Installation

1. **Download the project code locally**
```
git clone https://github.com/alfred-kctang/Fyyur.git
```

2. **Install the dependencies:**
```
pip install -r requirements.txt
```

3. **Run the development server:**
```
export FLASK_APP=myapp
export FLASK_ENV=development # enables debug mode
python3 app.py
```

4. **Verify on the Browser**<br>
Navigate to project homepage [http://127.0.0.1:5000/](http://127.0.0.1:5000/) or [http://localhost:5000](http://localhost:5000)
