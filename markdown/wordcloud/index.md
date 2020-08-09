# How I made my word cloud

I think word clouds are a pretty reasonable way to graphically summarize content. When properly implemented, they provide a list of important terms and an easy way to discern how significant those terms are in the source text. I didn't really have anything else to feature on my home page, so a word cloud seemed like an apt way to encompass the content of my personal site without duplicating information available on one of the other pages.

To create a word cloud, I needed a way to obtain the rendered text of every page that I have. Because some parts of this website are programmatically rendered to HTML by my SSG (e.g. the portfolio page, posts like these), I wrote a quick function to find all `.html` files created as outputs. From there, I isolated the "content" areas of each page with BeautifulSoup. To further refine this text, I used NLTK's list of "stop words" to remove terms that aren't particularly important for the purpose of creating a summary (e.g. this, that, and, etc).

Once I had a list of words, it was time to actually create the cloud. Thankfully, theres the `wordcloud` Python module which can turn a string of text into an SVG. I wrote a simple function to create a color gradient that I like (#d8d8d8 to <span class="blue">#7cafc2</span>) and passed that along to the image generator.

When I first tested the setup, it worked about as well as I had expected: an image showed up on the home page. However, it wasn't very great to look at: the cloud was too short on mobile yet big enough on desktop that a user would need to scroll to see the whole thing. To accommodate these different screen sizes, I decided to render the cloud at different aspect ratios, from 1:10 to 49:10. Then, I wrote some quick JS to load in the SVG which would fit best on the page.

Although there isn't really much of note to summarize (one of the most common words is "site" for example), this was a fun thing to add, and I think it looks pretty cool.
