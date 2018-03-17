<p align="center">
<img src='https://i.imgur.com/0SEH9TD.png?1'>
</p>

<h1 align='center'>Product</h1>

NARC is a cheat detection system for the Canvas LMS, made, in part, as a senior-product for Discovery High School at Newton Conover.
It uses Canvas LMS API queries to collect data programmatically for input into both traditional machine learning
systems as well as some deep-learning systems - such as the autoencoder, which helps find anomalous testing data. This project is mainly
inspired by a massive lack in clarity and ease-of-use tools in Canvas's quiz events, which prevents
non technology literate teachers from using Canvas to its full extent.

<h1 align='center'>Setup</h1>


###### Prerequisites
---
```
Python - 3.5.x
```

###### Canvas Course Setup
---
On your canvas course page you have to enable quiz log auditing. This allows Canvas to track page focus
through built in Javascript, yielding valuable information about a user's activity during a test.

For more information on how to do this, follow this [guide](https://community.canvaslms.com/docs/DOC-13029-4152156575)

###### Clone Repository
---
Open a CMD and type the following command:
```
git clone https://www.github.com/byrdofafeather/NARC
```
Once cloned, you can check branches with the following command:
```
git checkout <branch name here>
```

###### Install Requirements
---
In the newly cloned directory, run:
```
sudo pip install -r 'requirements.txt'
```
Important: if you are on Windows, running this command will not install the proper
version of numpy or all of the dependencies for scikit-learn. For both of these,
you will need to install pre-built wheel files for
[numpy+mkl](https://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy),
[scipy](https://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy),
and if you haven't got it already installed,
[sklearn](https://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-learn).

###### Setup Secrets
---
Create a new file in /Data-Processing/ called secrets.py <br>
In this file place a list of your api keys
```py
keys = ['insert canvas api token here']
```
If you need help getting a token, follow this [guide](https://community.canvaslms.com/docs/DOC-10806-4214724194)
 from Canvas

<h1 align='center'>Gathering Data</h1>

Data is gathered from subclasses of the Collector class <br>
```py
discussion_example = collectors.Discussion(discussion_id, class_id, header, url)
print(discussion_example.get_discussion())

quiz_example = collectors.Quiz(quiz_id, class_id, header, url)
print(quiz_example.get_quiz_events())
```
Collector classes can also be combined to get all of a certain type of item
in a module. <br>
```py
example_module = collectors.Module(module_id, class_id, header, url)
all_module_items = example_module.get_module_items()

quiz_list = []
for quiz in all_module_items['Subsections']['Quizzes']:
    quiz_list.append(collectors.Quiz(quiz,
                                    example_module.class_id,
                                    example_module.url,
                                    example_moudle.header))
```
<h1 align='center'>Building Datasets</h1>

Datasets are built in constructor classes.
For example, using the quiz constructor, a data set can be built
automatically without need for any additional information when given
a quiz class.

```py
example_quiz = Quiz(class_id=class_id, quiz_id=quiz_id, url=url, header=header)
example_quiz_data_set = example.quiz.build_dataframe()
```
This returns a fully functional Pandas Dataframe that can be fed into
sci-kit learn or tensorflow algorithms.

<h1 align='center'>Building Models</h1>

Machine Learning Models can be constructed from the data frames built
in the previous section. The predictor classes found in ModelTraning can be
used as templates in making certain types of model.

```py
predictor_example = AutoEncoder(example_quiz_data_set, anon=False)
anomalies = predictor_example.seperate()
```
This runs the data through the default 3-layer AutoEncoder with
hyperbolic tangent functions for every layer save for a linear layer
on the last hidden layer. The output of this function can then be run
through a K-Means separator to attempt to find the cheaters from high or
low performing student anomalies.

```py
example_cluster = KMeansSeparator(anomalies)
example_results = example_cluster.classify()
```
The results will then be returned as a dataframe with either the user
ID as the index or the user name. The data will contain the original testing data with a
sci-kit learn standard scalar applied to it and the predicted cluster (by default there will
either be 1 or 0).


<h1 align='center'>Related Works</h1>

* Canvas LMS Discussions Data Analytics: http://ceur-ws.org/Vol-1925/paper11.pdf
* Cheat Detection from Anomaly Detection: https://www.youtube.com/watch?v=Q2HLPCBStLQ

<h1 align='center'>License</h1>

MIT License, See [License.md](https://github.com/ByrdOfAFeather/NARC/blob/master/LICENSE) for details
