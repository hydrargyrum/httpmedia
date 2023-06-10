<%
    from urllib.parse import quote
%>

    <div class="slideshow"></div>

    <div class="slideshow-items">
% for sub, thumb in items.items():
    % if thumb:
        <a href="{{quote(sub.name)}}" style="display: none;">
            <img src="{{ base_url }}/thumb/{{thumb}}" loading="lazy" />
        </a>
    % end
% end
    </div>
