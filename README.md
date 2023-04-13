# CS22 Main

A web application for the project CLO

## Description - CLO

Scottish print portal – an online gateway to bridge the gap between analog and digital worlds, supporting the community which coexist at the cross-section

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install django and stripe.

```bash
pip install django
pip install stripe
```

Clone the repository into your desired location, and run the following commands

```bash
git clone https://stgit.dcs.gla.ac.uk/team-project-h/2021/cs22/cs22-main
cd boomsaloon
```
## Dependencies

The dependencies can be found in the requirements.txt file.
To install them, run the following command:

```bash
pip install -r requirements.txt
```

## Set up

Make sure you are in the directory ~/cs22-main/boomsaloon/ and execute the following in a command prompt
```bash
python manage.py makemigrations
python manage.py migrate
```

Optionally, to populate the database with sample data, run the following command
```bash
python populate_mags.py
```
## Executing program

```bash
python manage.py runserver
```

Open your browser and navigate to your localhost URL to view the page. 


#### Additional: Testing

Unit testing has been provided, run it with the following command

```bash
python manage.py test magportal.tests
```

## Authors

Contributors names and contact info:

Zhaohan Meng
2582280m@student.gla.ac.uk

Gunraj Gulati
2502903g@student.gla.ac.uk

Robbie Edgar
2461502e@student.gla.ac.uk

Nathan Pham
2439753p@student.gla.ac.uk

## Acknowledgements
*  [Django](https://www.djangoproject.com/) - A high-level Python Web framework that encourages rapid development and clean, pragmatic design.
*  [Stripe](https://stripe.com/gb) - Online payment processing technology for internet businesses
*  [jQuery](https://github.com/jquery/jquery) - A lightweight, "write less, do more", JavaScript library.

## License

[Apache](https://www.apache.org/licenses/LICENSE-2.0)
