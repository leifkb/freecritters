<%def name="formsuccess(**kwargs)">
    % for key in kwargs:
        % if key in fc.req.args:
<p class="formsuccessful">${kwargs[key]}</p>
        % endif
    % endfor
</%def>