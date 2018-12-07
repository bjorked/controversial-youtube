## controversial-youtube
Uses the Youtube API to find specified channel's most controversial videos.

# How to use:
```
application.py [-h] [--count count] channel

mandatory arguments:
  channel               channel's name

optional arguments:
  -h, --help              show this help message and exit
  --count count      amount of videos to print
```

# Example:
```
$ python application.py theneedledrop --count 3
1. The Weeknd- House of Balloons ALBUM REVIEW
Link: https://www.youtube.com/watch?v=OwxUIz-Thwc
Likes: 1299 Dislikes: 4085
Ratio: 75.87
2. Kanye West- My Beautiful Dark Twisted Fantasy ALBUM REVIEW
Link: https://www.youtube.com/watch?v=Jo4S2qlQGs0
Likes: 6098 Dislikes: 17032
Ratio: 73.64
3. Saba - CARE FOR ME ALBUM REVIEW
Link: https://www.youtube.com/watch?v=UAAxRBo4PsQ
Likes: 1505 Dislikes: 4124
Ratio: 73.26
```
