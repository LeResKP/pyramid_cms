<!DOCTYPE html>
<html>
<head>
  <title>The Pyramid Web Application Development Framework</title>
</head>
<body>
  <div id="wrap">
    <div id="top">
      <div class="top align-center">
        <div><img src="${request.static_url('pyramid_cms:static/pyramid.png')}" width="750" height="169" alt="pyramid"/></div>
      </div>
    </div>
    <div id="middle">
      <p>
        Login Page
        ${widget.display() | n}
      </p>
    </div>
</body>
</html>
