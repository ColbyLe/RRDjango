from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
# Create your views here.


def homepage(request):
    newsFeed = NewsFeed.objects.raw('SELECT * FROM website_newsfeed ORDER BY DATE DESC limit 10')
    comics = Comic.objects.raw('SELECT ComicID, ComicIssueTitle FROM website_comic '
                               'ORDER BY ComicRating DESC LIMIT 10;')
    return render(request, 'homepage/homepage.html', {'newsFeeds': newsFeed , 'comics': comics })


def get_comicpage(request):
    comicId = request.GET.get('id')
    userId = request.user.id
    if 'rate' in request.POST:
        userRating = int(request.POST.get("rating", None))
        comic = Comic.objects.get(ComicID=comicId)
        #rate, created = UserRatings.objects.update_or_create(id=userId, ComicID=comicId, defaults={'UserRating': userRating})
        try:
            rate = UserRatings.objects.get(id=userId, ComicID=comicId)
            comic.ComicTotalRating = int(comic.ComicTotalRating) + userRating - int(rate.UserRating)
            rate.UserRating = userRating
            rate.save(update_fields=["UserRating"])
        except:
            rate = UserRatings.objects.create(id=userId, ComicID=comicId, UserRating=userRating)
            if comic.ComicTotalRating:
                comic.ComicTotalRating = int(comic.ComicTotalRating) + userRating
            else:
                comic.ComicTotalRating = userRating
            if comic.ComicNumberOfRaters:
                comic.ComicNumberOfRaters = comic.ComicNumberOfRaters + 1
            else:
                comic.ComicNumberOfRaters = 1

        #rate = UserRatings(id=userId, ComicID=comicId, UserRating=userRating)


        #raters = UserRatings.objects.raw('SELECT id, UserRating, ComicID FROM website_userratings '
        #                                 'WHERE ComicID = %s;', [comicId])
        #numRaters = len(list(raters))
        #totalRating = 0
        #for rating in raters:
        #    totalRating = totalRating + rating.UserRating
        if comic.ComicNumberOfRaters != 0:
            comic.ComicRating = int(comic.ComicTotalRating) / comic.ComicNumberOfRaters
        else:
            comic.ComicRating = 0

        comic.save(update_fields=["ComicRating", "ComicTotalRating", "ComicNumberOfRaters"])


    #Reviews
    reviewList = Reviews.objects.raw('SELECT * FROM website_reviews '
                                     'WHERE ComicID = %s ORDER BY ReviewDate DESC', [comicId])
    userList = Users.objects.raw('SELECT * FROM auth_user')
    if "review" in request.POST:
        reviewtext = request.POST.get("textfield", None)
        revDate = timezone.now()
        user = request.user.username
        review = Reviews(ComicID=comicId, UserID=userId, username=user, ReviewDate=revDate,
                         ReviewText=reviewtext)
        review.save()

    comicList = Comic.objects.raw('select * from website_comic where ComicID = %s', [comicId])
    characterList = Character.objects.raw('SELECT DISTINCT Characters.CharacterID, CharacterName FROM website_comic '
                                       'INNER JOIN ComicCharacters ON website_comic.ComicID = ComicCharacters.ComicID '
                                       'INNER JOIN Characters ON ComicCharacters.CharacterID = Characters.CharacterID '
                                       'WHERE website_comic.ComicID = %s', [comicId])
    series = Series.objects.raw('SELECT DISTINCT ComicID, Series.SeriesID, Series.SeriesName FROM website_comic '
                                    'INNER JOIN Series ON website_comic.SeriesID = Series.SeriesID '
                                    'WHERE ComicID = %s', [comicId])
    publisher = Publishers.objects.raw('SELECT DISTINCT website_comic.ComicID, Publishers.PublisherID, Publishers.PublisherName FROM website_comic '
                                      'INNER JOIN Publishers ON website_comic.PublisherID = Publishers.PublisherID '
                                      'WHERE website_comic.ComicID = %s', [comicId])
    storyArcList = StoryArcs.objects.raw('SELECT DISTINCT StoryArcs.StoryArcID, StoryArcTitle FROM website_comic '
                                         'INNER JOIN ComicStoryArcs ON website_comic.ComicID = ComicStoryArcs.ComicID '
                                         'INNER JOIN StoryArcs ON ComicStoryArcs.StoryArcID = StoryArcs.StoryArcID '
                                         'WHERE website_comic.ComicID = %s', [comicId])
    writerList = Series.objects.raw('SELECT DISTINCT * FROM website_comic '
                                 'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                 'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                 'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                 'WHERE website_comic.ComicID = %s AND CreatorTypeName = "Writer";', [comicId])
    pencillerList = Series.objects.raw('SELECT DISTINCT * FROM website_comic '
                                 'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                 'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                 'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                 'WHERE website_comic.ComicID = %s AND CreatorTypeName = "Penciller";', [comicId])
    inkerList = Series.objects.raw('SELECT DISTINCT * FROM website_comic '
                                 'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                 'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                 'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                 'WHERE website_comic.ComicID = %s AND CreatorTypeName = "Inker";', [comicId])
    coloristList = Series.objects.raw('SELECT DISTINCT * FROM website_comic '
                                 'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                 'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                 'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                 'WHERE website_comic.ComicID = %s AND CreatorTypeName = "Colorist";', [comicId])
    lettererList = Series.objects.raw('SELECT DISTINCT * FROM website_comic '
                                 'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                 'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                 'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                 'WHERE website_comic.ComicID = %s AND CreatorTypeName = "Letterer";', [comicId])
    editorList = Series.objects.raw('SELECT DISTINCT * FROM website_comic '
                                 'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                 'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                 'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                 'WHERE website_comic.ComicID = %s AND CreatorTypeName = "Editor";', [comicId])
    coverArtistList = Series.objects.raw('SELECT DISTINCT * FROM website_comic '
                                 'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                 'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                 'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                 'WHERE website_comic.ComicID = %s AND CreatorTypeName = "Cover Artist";', [comicId])

    return render(request, 'comicpage.html', {'comic': comicList[0], 'characterList': characterList,
                                              'series': series[0], 'publisher': publisher[0],
                                              'storyArcList': storyArcList, 'writerList': writerList,
                                              'pencillerList': pencillerList, 'inkerList': inkerList,
                                              'coloristList': coloristList, 'lettererList': lettererList,
                                              'editorList': editorList, 'coverArtistList': coverArtistList,
                                              'reviewList': reviewList, 'userList': userList})


def get_characterpage(request):
    characterId = request.GET.get('id')
    characterList = Character.objects.raw('SELECT * FROM Characters WHERE CharacterID = %s', [characterId])
    comicList = Comic.objects.raw('SELECT DISTINCT website_comic.ComicID, ComicIssueTitle FROM website_comic '
                                   'INNER JOIN ComicCharacters ON website_comic.ComicID = ComicCharacters.ComicID '
                                   'INNER JOIN Characters ON ComicCharacters.CharacterID = Characters.CharacterID '
                                   'WHERE Characters.CharacterID = %s', [characterId])
    return render(request, 'characterpage.html', {'character': characterList[0], 'comicList': comicList})


def get_creatorpage(request):
    creatorId = request.GET.get('id')
    creator = Creator.objects.raw('SELECT * FROM Creators WHERE CreatorID = %s', [creatorId])
    writerList = Comic.objects.raw('SELECT DISTINCT website_comic.ComicID, ComicIssueTitle, Creators.CreatorName FROM website_comic '
                                   'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                   'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                   'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                   'WHERE Creators.CreatorID = %s AND CreatorTypeName = "Writer"', [creatorId])

    pencillerList = Comic.objects.raw('SELECT DISTINCT website_comic.ComicID, ComicIssueTitle, Creators.CreatorName FROM website_comic '
                                   'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                   'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                   'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                   'WHERE Creators.CreatorID = %s AND CreatorTypeName = "Penciller"', [creatorId])

    inkerList = Comic.objects.raw('SELECT DISTINCT website_comic.ComicID, ComicIssueTitle, Creators.CreatorName FROM website_comic '
                                   'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                   'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                   'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                   'WHERE Creators.CreatorID = %s AND CreatorTypeName = "Inker"', [creatorId])

    coloristList = Comic.objects.raw('SELECT DISTINCT website_comic.ComicID, ComicIssueTitle, Creators.CreatorName FROM website_comic '
                                   'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                   'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                   'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                   'WHERE Creators.CreatorID = %s AND CreatorTypeName = "Colorist"', [creatorId])

    lettererList = Comic.objects.raw('SELECT DISTINCT website_comic.ComicID, ComicIssueTitle, Creators.CreatorName FROM website_comic '
                                   'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                   'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                   'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                   'WHERE Creators.CreatorID = %s AND CreatorTypeName = "Letterer"', [creatorId])

    editorList = Comic.objects.raw('SELECT DISTINCT website_comic.ComicID, ComicIssueTitle, Creators.CreatorName FROM website_comic '
                                   'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                   'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                   'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                   'WHERE Creators.CreatorID = %s AND CreatorTypeName = "Editor"', [creatorId])

    coverArtistList = Comic.objects.raw('SELECT DISTINCT website_comic.ComicID, ComicIssueTitle, Creators.CreatorName FROM website_comic '
                                   'INNER JOIN ComicCreators ON website_comic.ComicID = ComicCreators.ComicID '
                                   'INNER JOIN Creators ON ComicCreators.CreatorID = Creators.CreatorID '
                                   'INNER JOIN CreatorTypes ON ComicCreators.CreatorTypeID = CreatorTypes.CreatorTypeID '
                                   'WHERE Creators.CreatorID = %s AND CreatorTypeName = "Cover Artist"', [creatorId])
    return render(request, 'creatorpage.html', {'creator': creator[0], 'writerList': writerList,
                                                'pencillerList': pencillerList, 'inkerList': inkerList,
                                                'coloristList': coloristList, 'lettererList': lettererList,
                                                'editorList': editorList, 'coverArtistList': coverArtistList})


def get_newsfeedpage(request):
    newsFeedID = request.GET.get('id')


    news = NewsFeed.objects.get(ID=newsFeedID)

    news.Text = news.Text.replace("||||", "\n")
    #print(news.Text)
    news.save(update_fields=["Text"])
    newsFeed = NewsFeed.objects.raw('select * from website_newsfeed where ID = %s', [newsFeedID])
    return render(request, 'newsfeedpage.html', {'newsFeed': newsFeed[0]})


def get_comic(request):
    comics = Comic.objects.raw('SELECT Series.SeriesID, website_comic.ComicID, Series.SeriesName, ComicIssueTitle '
                               'FROM website_comic '
                               'INNER JOIN ComicSeries ON website_comic.ComicID = ComicSeries.ComicID '
                               'INNER JOIN Series ON ComicSeries.SeriesID = Series.SeriesID '
                               'ORDER BY SeriesName ASC, ComicIssueTitle ASC')
    return render(request, 'comic.html',{'comics': comics})


def get_character(request):
    characters = Character.objects.raw('SELECT CharacterID, CharacterName FROM Characters ORDER BY CharacterName ASC')
    return render(request, 'character.html', {'characters': characters})


def get_creator(request):
    creators = Creator.objects.raw('SELECT CreatorID,CreatorName,CreatorDOB FROM Creators ORDER BY CreatorName ASC')
    return render(request, 'creator.html', {'creators': creators})


def get_newsfeed(request):
    newsFeed = NewsFeed.objects.raw('SELECT * FROM website_newsfeed ORDER BY DATE DESC')
    return render(request, 'newsfeed.html', {'newsFeed': newsFeed})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('homepage')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


#def rate_comic(request, rating):
#    pass
#def post_comment():


def get_profile(request):
    userId = request.GET.get('id')
    user = Users.objects.raw('SELECT * FROM auth_user WHERE id = 10')
    return render(request, 'profile.html', {'user': user[0]})


def get_signuppage(request):
    return render(request, 'signup.html')


def get_about(request):
    return render(request, 'about.html')


