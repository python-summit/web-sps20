# Static Website for the Swiss Python Summit

See [www.python-summit.ch](https://www.python-summit.ch/)

A [Lektor](https://www.getlektor.com/) powered project.

## Development

To run the website:

* Clone the repository
* Install requirements with `make install`
* Run Lektor server with `make serve`

After that the website should be available on port 5000.

### How to add a talk recording

- Go to http://localhost:5000/admin/root:talk-recordings/edit
- Click "Add Page"
- Choose the "Recording" model
- Set the "Title" field to the talk title
- Click "Add Child Page"
- Fill in the data and save
- Click "Add Attachment"
- Upload PDF file with slides
- Click on the attachment in the left navigation
- Change the attachment type to "Slides"

Note: The playlist URLs are stored in `databags/playlists.json`.
