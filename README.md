# reliability
Take a look at how changing maintenance interval can impact asset reliability!

You can access the app through this [link](https://reliability-demo.herokuapp.com)
___

If you decide to run the whole thing yourself...

## Choice A: Docker!
Build using the `Dockerfile` provided. After running the container built on the image, there will be a pop-up screen on your browser. If not, you can follow the link in the command line output.

It will require `python:3.7-slim-buster` Debian Buster image for Python, else it will be a little bit slower to build. Also apologize for the long list of dependencies (mostly because of SciPy, sigh).

## Choice B: Manual
### Virtual Environment
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

### Streamlit
Upon installation, `streamlit` is also registered as a command. To run Streamlit on a localhost:

`streamlit run src/main.py`

It should automatically pop-up in your preferred browser, running in port 8501 as a default.
