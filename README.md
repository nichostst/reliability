# reliability
Take a look at how changing maintenance interval can impact asset reliability!

You can access the app through this [link](https://reliability-demo.herokuapp.com)
___

If you decide to run the whole thing locally...

## Basic How-Tos
Create a virtual environment - this is pretty standard. Recommended to use virtualenv if you have it installed.

`pip install virtualenv`

Navigate to the `reliability` directory (this is where we will do e-ve-ry-thing) and type

`virtualenv <your env name>`<br>
`source <your env name>/bin/activate`

to create and activate the virtual environment. Next,

`pip install -r requirements.txt`

to install all the dependencies. The script is now ready to run!

After all the fun, you can deactivate the virtual environment by typing
`deactivate`.

## Streamlit
Upon installation, `streamlit` is also registered as a command. To run Streamlit on a localhost:

`streamlit run src/main.py`

It should automatically pop-up in your preferred browser, running in port 8501 as a default.
