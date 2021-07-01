# Table of Contents
- [Table of Contents](#table-of-contents)
- [MuMe](#mume)
  - [Features](#features)
  - [Standard Flow](#standard-flow)
  - [API Integration](#api-integration)
  - [Technology Stack](#technology-stack)


# [MuMe](https://musicandmentalhealth.herokuapp.com/)

[MuMe](https://musicandmentalhealth.herokuapp.com/) is a Music & Mental Health Community designed as a safe space for people to publicly express themselves through music to complement written words. Members can use [MuMe](https://musicandmentalhealth.herokuapp.com/) as a virtual journal as well as a social platform to discover others who may be able to relate to their content.

What makes [MuMe](https://musicandmentalhealth.herokuapp.com/) special is the members' ability to search for a song (based on their current mood) and add it to their posts. With music being a universal language, I believe people sharing a song that represents their current mood can be more powerful than spoken (or in this case, written) words.


## Features
- When the User creates a new post, they have the option to search for a song and add it to their post.
  - As I mentioned above, music is a universal language, so I implemented this song-search function to allow people to express themselves through the song of their choice.
    - I know what you're thinking... Yes, I had a MySpace... and yes, I'm definitely bringing some MySpace vibes back.
  - At some point, I intend to add a comment function so users have the option of discussing their music tastes.
    

## Standard Flow

- Visitors sign-up for/log-in to account.
- You may create a new post.
  - Share whatever you want in the textbox.
  - Search for a song that best suits your mood and simply click "SELECT".
  - Click "Publish".
- Your post is now live on your profile page and your home page.
- You can view other MuMe members' posts and they can see yours.
- Posts include separate links that take you to the song and artist page on Spotify.
- You may search for other MuMe members and Follow/Unfollow.
- You may like/unlike other members' posts and they can do the same to yours.
- You can delete your posts.
- You may edit/delete your profile.
- If you haven't deleted your profile, you may log-out.


## API Integration

[Spotify Web API](https://api.spotify.com)


## Technology Stack

- Python
  - Flask
  - Flask-WTForms
  - SQLAlchemy
  - Bcrypt
  - Jinja
- JavaScript
  - JQuery
  - Axios
- HTML
- CSS
  - Bootstrap
  - Font Awesome
