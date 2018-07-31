import json
import re
import pandas as pd
from textblob import TextBlob
from tqdm import tqdm_notebook as tqdm
import plotly.graph_objs as go
from fuzzywuzzy import fuzz
import calendar
from datetime import timedelta

class Conversation:
    def __init__(self, messages=None, verbose=False, neutral=False):
        if messages is None: # changed
            messages = []
        self.messages = messages
        self.verbose=verbose
        self.neutral=neutral

    clean = lambda self, text: ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())
    get_sentiment =  lambda self, text: TextBlob(self.clean(text)).sentiment

    def get_names(self):
        names = []
        for message in self.messages:
            if 'sender_name' in message:
                names.append(message['sender_name'])
        return set(names)

    def get_tags(self):
        tags = []
        for message in self.messages:
            if 'tag' in message:
                tags.append(message['tag'])
        return set(tags)

    def load(self, filename, tag=None, participants=None):
        with open(filename) as file:
            self.content = json.load(file)

            try:
                if tag==None:
                    tag = self.content['title']
                if participants==None:
                    participants = json.dumps(self.content['participants'])
            except KeyError, e:
                if self.verbose:
                    print "Error loading title and participants in %s" % filename

            self.content = self.content['messages']

            for i in tqdm(range(0,len(self.content)), leave=False):
                try:
                    senti_subjecti = self.get_sentiment(self.content[i]['content'])
                    if 'timestamp' not in self.content[i] and 'timestamp_ms' in self.content[i]:
                        self.content[i]['timestamp'] = self.content[i]['timestamp_ms']/1000.0
                    self.content[i]['tag'] = tag
                    self.content[i]['participants'] = participants
                    self.content[i]['sentiment'] = senti_subjecti.polarity
                    self.content[i]['subjectivity'] = senti_subjecti.subjectivity
                    if self.neutral == True or self.content[i]['sentiment'] != 0.0:
                        self.messages.append(self.content[i])
                except KeyError, e:
                    if self.verbose:
                        print "KeyError in file %s" % (filename)

    def get_df(self):
        df = pd.DataFrame(self.messages)
        if 'timestamp_ms' in df and 'timestamp' not in df: ## Last minute fix because facebook changed formats on us
            df['timestamp'] = [val/1000.0 for val in df['timestamp_ms']]
        if 'timestamp' in df:
            df['Date_Time'] = pd.to_datetime(df['timestamp'],unit='s')
        return df.set_index("Date_Time")

    def get_stats(self, extended=False):
        stats = dict()
        stats['names'] = self.get_names()
        stats['tags'] = self.get_tags()
        stats['length'] = len(self.messages)
        stats['neutral'] = self.neutral

        if extended:
            participants = []
            for message in self.messages:
                if 'participants' in message:
                    participants.append(message['participants'])
            stats['participants'] = set(participants)

        return stats

    def search_names(self, name):
        return sorted(self.get_names(),
                      key=lambda cur_name: fuzz.token_sort_ratio(cur_name, name),
                      reverse=True)

    def filter_by_name(self, names, including=True):
        filtered = []
        for message in self.messages:
            if 'sender_name' in message:
                included = message['sender_name'] in names
                if (including and included) or (not including and not included):
                    filtered.append(message)
        return Conversation(filtered, self.verbose, self.neutral)

    def filter_by_tag(self, tags, including=True):
        filtered = []
        for message in self.messages:
            if 'tag' in message:
                included = message['tag'] in tags
                if (including and included) or (not including and not included):
                    filtered.append(message)
        return Conversation(filtered, self.verbose, self.neutral)

    def filter_by_datetime(self, start, end=None):
        start_timestamp = calendar.timegm(start.timetuple())
        end_timestamp = calendar.timegm(end.timetuple()) if end != None else None
        return self.filter_by_timestamp(start_timestamp, end_timestamp)

    def filter_by_sentiment(self, begin=-1.0, end=1.0, including=True):
        filtered = []
        for message in self.messages:
            included = message['sentiment'] >= begin and message['sentiment'] <= end
            if (including and included) or (not including and not included):
                filtered.append(message)
        return Conversation(filtered, self.verbose, self.neutral)

    def filter_by_timestamp(self, start, end=None):
        if end != None and start > end:
            tmp = start
            start = end
            end = tmp
        filtered = []
        for message in self.messages:
            if 'timestamp' in message:
                if message['timestamp'] >= start:
                    if end is None or message['timestamp'] <= end:
                        filtered.append(message)
        return Conversation(filtered, self.verbose, self.neutral)

    def save_csv_utf8(self, filename):
        self.get_df().to_csv(filename, encoding='utf-8')

    def annot_highlow(self, smadf, rangedf, selected_row):
        highrow = rangedf.loc[rangedf['sentiment'].idxmax()]
        lowrow  = rangedf.loc[rangedf['sentiment'].idxmin()]
        currow  = smadf.iloc[[selected_row]]
        annot = "High: %s - %s<br>Cur: %s - %s<br>Low: %s - %s" % (
            highrow['sender_name'], highrow['content'],
            currow['sender_name'][0],  currow['content'][0],
            lowrow['sender_name'],  lowrow['content']
        )
        return annot

    def annot_current_with_subjectivity(self, smadf, rangedf, selected_row):
        currow  = smadf.iloc[[selected_row]]
        annot = "From:%s<br>Sentiment:%s<br>Subjectivity:%s<br>Content:%s" % (
            currow['sender_name'][0], currow['sentiment'][0], currow['subjectivity'][0], currow['content'][0],
        )
        return annot

    def add_density_cloud(self, messagedf, smadf, time_units, timeframe, annotation=None):
        seconds_per_unit = {"S": 1, "M": 60, "H": 3600, "D": 86400, "W": 604800, "Y": 31536000}
        seconds = int(time_units*seconds_per_unit[timeframe])/2
        density = []
        annot=[]
        for i in range(0, len(smadf)):
            rangedf = messagedf.loc[
                (messagedf.index >= smadf.index[i]-timedelta(seconds=seconds)) &
                (messagedf.index <= smadf.index[i]+timedelta(seconds=seconds))
            ]
            density.append(len(rangedf))
            if annotation!=None:
                annot.append(annotation(smadf, rangedf, i))
        maxdensity = max(density)
        density = [float(d)/maxdensity for d in density]
        smadf['density'] = density
        if annotation!=None:
            smadf['annotation'] = annot

    def plot(self, timeframe = 'D', ohlc = False, smas = [1], ohlc_colors = ['#17BECF', '#7F7F7F'],
             density=False, annotation=None, label=""):
         oldsmas = smas
        if label!="":
            label += " - "
        if timeframe == 'W':
            timeframe = 'D'
            smas = [j*7 for j in smas]
        messagedf = self.get_df().sort_index() # Possibly speed up or cache
        resampled = messagedf.resample('1'+timeframe)
        ohlcdf = resampled[['sentiment']].ohlc()['sentiment']
        plots = []
        if ohlc:
            plots.append(
                go.Ohlc(
                    x=ohlcdf.index,
                    open=ohlcdf.open,
                    high=ohlcdf.high,
                    low=ohlcdf.low,
                    close=ohlcdf.close,
                    increasing=dict(line=dict(color= ohlc_colors[0])),
                    decreasing=dict(line=dict(color= ohlc_colors[1])),
                    name="OHLC",
                    yaxis='y2'))
        for sma in smas:
            smadf = messagedf[['sentiment']].rolling(str(sma)+timeframe).mean()
            smaremoved = messagedf[messagedf.columns.difference(['sentiment'])]
            smadf = pd.concat([smadf, smaremoved], axis=1)
            if density or annotation:
                self.add_density_cloud(messagedf, smadf, sma, timeframe, annotation)
            if annotation != None:
                plots.append(go.Scatter(x=smadf.index, y=smadf['sentiment'], name="%sSMA%d"%(label,oldsmas[smas.index(sma)]), text=smadf['annotation']))
            else:
                plots.append(go.Scatter(x=smadf.index, y=smadf['sentiment'], name="%sSMA%d"%(label,oldsmas[smas.index(sma)])))
            if density:
                plots.append(go.Scatter(x=smadf.index, y=smadf['density'], name="%sDensity-SMA%d"%(label,oldsmas[smas.index(sma)])))

        return plots
