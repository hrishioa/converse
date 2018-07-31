# Converse

> Sentiment analysis and charting library supporting Messenger data dumps

Converse is a flexible charting library in python that makes sentiment analysis and charting easier. The aim is to provide strong functionality out of the box with minimal code while being configurable enough to support larger projects.



## Getting Started

```sh
pip install converse
```

That's all, really. For a walkthrough of the basic features, look here or in Demo.ipynb. For a ready-to-go installation with a (really small, faked) conversation, run:

```sh
docker pull hrishioa/converse
```



## Quickstart

Converse currently supports only facebook messenger (Whatsapp dump support is planned).

1. The first step is to download your chat data (use [one](https://www.imore.com/how-download-copy-your-facebook-data) [of](https://sea.pcmag.com/software/20441/feature/how-to-download-your-facebook-data-and-6-surprising-things-i) these guides to do so - make sure to pick JSON over HTML as the format), and unzip the archive. Converse is completely offline (even for plotting), and all your information is local.

2. Create new jupyter notebook (ideally in the messages directory) with

   ```sh
   jupyter notebook
   ```

3. The following piece of code should have you up and plotting:

   ```python
   from converse import Conversation
   from tqdm import tqdm_notebook as tqdm
   from plotly.offline import init_notebook_mode, iplot

   init_notebook_mode(connected=True)
   convo = Conversation()
   convo.load("path-to-message.json") # structure is usually archive-root/convo-name/message.json
   iplot(convo.plot())
   ```



### Built With

----

* [Textblob](https://textblob.readthedocs.io/en/dev/) - Sentiment Analysis
* [Pandas](https://pandas.pydata.org/) - data management
* [Plotly](https://plot.ly/python/) - graphing
* [FuzzyWuzzy](https://github.com/seatgeek/fuzzywuzzy) - string searching



### License

---

This project is licensed under GPLv3.



This project was cobbled together from tools built by the author in a weekend to do some standard sentiment analysis. Still very much in alpha, maybe even pre-alpha. Do submit any issues or problems, I'll do my best to patch!
