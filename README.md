# CityofBarberton.com
This is the source for the City of Barberton's public website. It is a fairly simple static website, the only actual code is on the client side (JavaScript).

## Interesting Portions
There is one portion of the site which may be of interest: the a poor man's site search.

### Why implement site search this way
This code-base represents the first major redesign of the City's website in probably a decade. The idea was to use the existing infrastructure, which included static site hosting, and yet perform as much modernization as possible as quickly as possible. Bootstrap, or Twitter Bootstrap, was used to create a responsive design and all of the dynamic content was pulled from third-party sites (Google, Twitter, etc.). The only required feature which could not be accomplished using this approach was site search, hence this approach.

### How is site search implemented
A Python script is ran on the development machine against the static HTML files; it generates a page list and a text index. This script first extracts contact information so that it can be specially presented in the search results. Next, the script extracts the text from the pages and uses the Python Natural Language Toolkit to extract useful information (remove common words and preserve word order for interesting phrases). The data generated from the Python script is stored in JSON files which are pulled to the browser when the client performs a search. The actual searching is performed in the clients browser.