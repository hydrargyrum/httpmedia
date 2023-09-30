<%
    from urllib.parse import quote
%>

% for sub, thumb in items.items():
    % if thumb:
<div class="item">
    <a href="{{quote(sub.name)}}">
        <img class="thumbnail" src="{{ base_url }}/thumb/{{thumb}}" loading="lazy" />
        <span class="label">
            {{sub.name}}
        </span>
    </a>
</div>

    % else:

<div class="item">
    <a href="{{quote(sub.name)}}{{"/" if sub.is_dir() else ""}}">
        <span class="label">
            {{sub.name}}{{"/" if sub.is_dir() else ""}}
        </span>
    </a>
</div>

    % end
% end
