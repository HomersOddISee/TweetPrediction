#The point of this python script/programm is to predict the number of likes and retweets you'll get on a twitter post. This is done by reading your tweets, building a mathematical model of the data, and using that to predict an outcome

import tweepy #This twitter module is used to communicate with the twitter REST API.
import numpy as np #A math module which is partly used to build a mathematical model
import matplotlib.pyplot as plt #A plot module which adds the functionality of the app to represent the users tweet data as a scatter plot 
import math #Another math module used for building the model
import scipy #This provides a scientific toolkit of functions which can be used for building the mathematical module
from scipy.interpolate import interp1d #From the previous, a tool which interpolates data
import time #A simple module which is only used in this programm to delay while the user interacts with the program
import webbrowser #A module whice is used to open URL's in the default webbrowser




Dummy=False#This is a dummy argument which keeps my programming permanently running unless the user quits the programm
DataAquired=False #This acts to determine whether I have obtained the user's tweet data
TweetEntered=False # A boolen which determine whether the user has entered a tweet
Restart=False #A boolean which is used to keep a second part of my programm running where the user interacts 
UserResponseBool=False #A boolean used in keeping the user response loop

while Dummy==False:
    while DataAquired==False:
        #This allows for authentication so that my app may be able to access your tweets and 'read' them. My app only has permission to read the users tweets.
        #Full documentation on my app's persmissons can be found at 'https://dev.twitter.com/oauth/application-only'.
        #My app is called "Twitter Tweet Prediction" for the purpose of this project.
        
        #You will aslo need to vist the following URL "https://dev.twitter.com/overview/status" to check if the RestAPI is currently available or under temporary maintenance. #If under maintence I kindly ask that you wait till it's functional.It's typically a 30 minute to hour break.
        #The programm will not function if the API is down. If error 429 pops up, the user has made too many requests in a time interval and must wait 15 minutes
        

        #Authentication. This part of my code requires the user to allow access for my app to read tweets. 

        Auth=tweepy.OAuthHandler(consumer_key,consumer_secret) #Consumer key and consumer secret are private for now
        AuthUrl=Auth.get_authorization_url()
        print("You must go to this url to authorize this app: "+AuthUrl)
        time.sleep(3)
        webbrowser.open_new(AuthUrl)
        AuthToken=str(input("And then enter the 7 digit code you get here: "))
        id=str(input("Also enter your user ID: @") )
        print("This may take a while, just working with your tweets.")


        try:
            global AccessToken
            AccessToken=Auth.get_access_token(AuthToken)

        except tweepy.TweepError:
            print("Error! Failed to get access token. Check if you entered the right values and restart the module")
            break

        #After authentication, the API becomes functional. If authentication wasn't possible, the user entered a value incorrectly and must restart

        API=tweepy.API(Auth)

        #In this section I firstly obtain the tweet data, and I will mine for tweet "like" and "retweets" data. And then use it later for building a mathematical model
     
        APIResponse=[]
        for status in tweepy.Cursor(API.user_timeline,id,include_rts=False).items(500):#RT's set to false ensures I only  obtain the users tweets. Items is the number of tweet "nodes". The reason I chose the 500 most recent tweets is explained in the report 
            APIResponse.append(status)


        TweetText=[tweet.text for tweet in APIResponse]

        q=[]#A "dummy list" which acts as a way for different functions to communicate data with little commplication.
        def GenerateWords(List):
            for item in List:
                    q.append(item.lower().split(" "))

        GenerateWords(TweetText)   

        #I now want to convert my words in my list of words(q), which is nested in tweets(TweetText), to a list of characters, nested in q, nested in TweetText (3 dimensional list)
        #I take q which is in a form q=[tweet1[words],tweet2[Words],tweet3[words].....] and convert it to q=[tweet1[Word1[characters]],Word2[characters],[Word3[characters]]],tweet2[[Word1[characters]],[Word2[characters]],[Word3[characters]].....]

        TweetWordBreak=[[list(word) for word in tweet] for tweet in q]
        #I want to convert each character obtained in a word that has been listed to an integer

        TweetWordBreakInt=[[[ord(c) for c in word] for word in tweet] for tweet in TweetWordBreak] #The ord() function converts a character to it's unicode integer equivalent

        #The whole reason for this process is to assign an integer value to every word used in your tweets. This makes frequency and probability analysis incredibly easier.I will calculate each words integer value using the mean of integer characters

        TweetWordBreakAvg=[[float(sum(word)/len(word)) if len(word)>0 else word==float(0) for word in tweet] for tweet in TweetWordBreakInt]

        #Now each tweet has been converted to a list of unique integers which represent the equivalent words.
        #I can now use these integers and analyse the language used mathematically. I decided that the best way to understand a tweets language is by knowing the distribution of the words.
        #From this we can see that a tweet's popularity is determined by the words in it but also how they're arranged. This eliminates the requirement to remove stop words as they're integral to sentence structure
        #When I first started this project I wrote code that would involve eliminating stop word/connectives by using a list of Stop words and a defined function as follows.
        """
            def CleanText(NestedList):
                for item in NestedList:
                    for word in item:
                       if word in StopWords:
                           item.remove(word)

           CleanText(q)""" 
        #To analyse language distribution I decided to use some joint probability distribution function. I calculated the standard deviation of each tweet

        def StandDev(NestedIntegerList):
            global StandDevList
            StandDevList=[]
            for item in NestedIntegerList:
                StandDevList.append(np.std(item))
          

        StandDev(TweetWordBreakAvg)
        StandDevTweets=[math.log(x) if x>0 else x for x in StandDevList] #The standard deviation for each tweet was logged to create a more reasonable scale later for the scatter plots

        RTCountData=[tweet.retweet_count for tweet in APIResponse] #Retweet count data 
        FavCountData=[tweet.favorite_count for tweet in APIResponse] #Favourite Count data
    
        plt.scatter(StandDevTweets,RTCountData,label="Number of retweets to word spread",marker='o')
        plt.scatter(StandDevTweets,FavCountData,label="Number of favourites to word spread",marker='^')
        plt.axis([0,max(StandDevTweets),0,max(RTCountData+FavCountData)])
        plt.xlabel("Tweet integer equivalent in reverse chronological order")
        plt.ylabel("Retweet/Fav count")
        #This returns a history of the popularity of the tweets if the user is interested in seeing how many likes and favourites the get over a time period with most recent tweets being at the start of the plot

        DataAquired=True
        continue


    #The following asks the user to tell the programm what they want to tweet.

    while TweetEntered==False :
        global UserTweet
        UserTweet=str(input("So, what do you want to Tweet: "))
        if len(UserTweet)>140: #To keep tweet within character limit
            print("Your Tweet is too long")
        elif len(UserTweet)<140:
            Tweet=UserTweet.split(" ")
            TweetBreak=[list(word) for word in Tweet]
            TweetBreakNum=[[ord(c) for c in word] for word in Tweet]#Converting words to list of integers
            TweetBreakNumAvg=[float(sum(word)/len(word)) if len(word)>0 else word==float(0) for word in TweetBreakNum]#Converting words to there equivalent average
            StandDevNewTweet=np.std(TweetBreakNumAvg)
            TweetEntered=True
            break
        
    #Now knowing what the user wants to tweet as well as all their previous tweets and also knowing the RT and favourite count.
    
    #Interpolation of tweets to RT count
    TweetRTRelation=interp1d(StandDevTweets,RTCountData,kind='linear')#The third argument decides the type of function used to interpolate data. I observed that the RT and Fav data were best described by a linear function
    RTNewTweet=round(int(TweetRTRelation(math.log(StandDevNewTweet))))#Rounded as it will only be an integer, I now have the predicted number of retweets. StandDevNewTweet is logged to fit the scale

    #Interpolation of tweets to favourite count
    TweetFavRelation=interp1d(StandDevTweets,FavCountData,kind='linear')
    FavNewTweet=round(int(TweetFavRelation(math.log(StandDevNewTweet))))#Rounded as it will only be an integer, I now have the predicted number of fav

    print("This tweet: '"+UserTweet+ "' will get",
          str(RTNewTweet)+" retweets and ",
          str(FavNewTweet)+" favourites")
    
    #The main function of the app has finished. The next code is the end page of the programm. This asks the user how they would like to continue with the app.
    while Restart==False:
        
        UserResponse=str(input("Hope this was useful, do you want to analyse another a tweet?(yes/no)"))
        if UserResponse.lower()=="yes":
            print("Ok no problem")
            TweetEntered=False #Turns on the "So what do you want to tweet loop" 
            break
        elif UserResponse.lower()=="y":
            print("Ok,no problem.")
            TweetEntered=False
            break
        elif UserResponse.lower()=="no":
            while UserResponseBool==False:
                Plots=str(input("Do you want to see a plot of your tweet RT's and Fav?(yes/no)"))
                if Plots.lower=="yes":
                    print("Ok no problem.",quit)
                    plt.show()
                    break
                elif Plots.lower()=="y":
                    print("Ok no problem.",quit)
                    plt.show()
                    break
                elif Plots.lower()=="no":
                    print("Ok, hope to see you again.")
                    time.sleep(3)
                    quit()
                    break
                elif Plots.lower()=="n":
                    print("Ok, hope to see you again.")
                    time.sleep(3)
                    quit()
                    break
                else:
                    print("Please say 'yes or no' or 'y or n'.")
                    continue
        elif UserResponse.lower()=="n":
            while UserResponseBool==False:
                Plots=str(input("Do you want to see a plot of your tweet RT's and Fav?(yes/no)"))
                if Plots.lower=="yes":
                    print("Ok no problem.",quit)
                    plt.show()
                    break
                elif Plots.lower()=="y":
                    print("Ok no problem.",quit)
                    plt.show()
                    break
                elif Plots.lower()=="no":
                    print("Ok, hope to see you again.")
                    time.sleep(3)
                    quit()
                    break
                elif Plots.lower()=="n":
                    print("Ok, hope to see you again.")
                    time.sleep(3)
                    quit()
                    break
                else:
                    print("Please say 'yes or no' or 'y or n'.")
                    continue
        else:
            print("Please say 'yes or no' or 'y or n'.")
            continue
        
        

    
