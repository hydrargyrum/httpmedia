<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="{{ base_url }}/static/vendor-baguetteBox.min.css" />
    <script src="{{ base_url }}/static/vendor-baguetteBox.min.js"></script>

    <link rel="stylesheet" href="{{ base_url }}/static/style.css" />
    <link rel="stylesheet" href="{{ base_url }}/static/water.min.css" />
    <script src="{{ base_url }}/static/slideshow.js"></script>
</head>
<body>
    <a href="javascript:startCarousel()">Slideshow</a>

    <div class="items">
        % include("links", items=items)
    </div>

    % include("slideshow_items", items=items)

</body>
</html>
