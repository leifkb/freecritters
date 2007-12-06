<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">

<html lang="en">
<head>
	<title>404 - Not Found</title>
	<link type="text/css" rel="stylesheet" media="screen,projection" href="${fc.url('static', fn='error.css')}">
</head>
<body>
    <h1>404 - Not Found</h1>
    <p>The page you requested, <kbd>${fc.req.path}</kbd>, could not be found. If you followed a link here, it may be outdated.</p>
    <p>You may want to go to the <a href="${fc.url('home')}">${fc.req.config.site.name} home page</a>.</p>
</body>
</html>