<h1 align='center'>Product</h1>

NARC is a cheat detection system for the Canvas LMS, made, in part, as a senior-product for Discovery High School at Newton Conover.

<h1 align='center'>Steup</h1>

###### Prerequisites
```
Python - 3.5.x
```

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
in the newly cloned directory, run:
```
pip install -r 'requirements.txt'
```

###### Setup Secrets
---
Create a new file in /Data-Processing/ called secrets.py <br>
in this file place a list of your api keys
```py
keys = ['insert canvas api token here']
```

###### Temporary File Storage
---
Create a folder in /Data-Processing/ titled /temp/
this directory will store data when making new api calls is not needed

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



<h1 align='center'>Related Works</h1>

* Canvas LMS Discussions Data Analytics: http://ceur-ws.org/Vol-1925/paper11.pdf

<h1 align='center'>License</h1>

MIT License, See [License.md](https://github.com/ByrdOfAFeather/Senior-Product/blob/master/LICENSE) for details



