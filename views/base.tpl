<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/baguettebox.js/1.11.0/baguetteBox.min.css" integrity="sha256-cKiyvRKpm8RaTdU71Oq2RUVgvfWrdIXjvVdQF2oZ1Y4=" crossorigin="anonymous" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/baguettebox.js/1.11.0/baguetteBox.min.js" integrity="sha256-yQGjQhFs3LtyiN5hhr3k9s9TWZOh/RzCkD3gwwCKlkg=" crossorigin="anonymous"></script>

    <link rel="stylesheet" href="/static/style.css" />
    <script src="/static/slideshow.js"></script>
</head>
<body>
    <a href="javascript:startCarousel()">Slideshow</a>

    <div class="items">
        % include("links", items=items)
    </div>

    % include("slideshow_items", items=items)

</body>
</html>
