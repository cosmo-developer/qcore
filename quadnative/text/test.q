<html>
    <head>
        {{BOOTSTRAP.css_bundle_min}}
        <title>Quadnative | {{SITE.home_title}}</title>
    </head>
    <body bgcolor="{{BODY.bg_color}}" class="{{BODY}}">
        <div class="{{BOOTSTRAP.extra_layout}}">
            <div class="{{BOOTSTRAP.default_layout}}">
                <h2 style="text-align:center;">Using Bootstrap version: {{BOOTSTRAP.self}}</h2>
                <ul>
                <q.
                  Global f d=88 "Something";
                  Global data=(user1=(name="hello".Replace("h")With("H"),id=909),user2=(name="Roushan",id=88),user3=(name="Roushan",id=1));
                  Loop(data)Times(data.Length)Condition(true):[
                    Print("<li> User:",key,Space,value(` username:{name} and identification:{id}`),"</li>");
                  ]
                  donothing="this are murgi";
                  donothing.+="something more";
                  Print(donothing&Line);
                  data.user1.name.+=" World";
                  <#Print(Line&data.user1.name&Line);
                  Print(data.user1.name.End);#>
                  Print(Space(20),data.user1.name.Split(` `));
                  Print(data);
                  f=(2,3,4,5);
                  Loop(f)Times(f.Length)Condition(true):[
                    Print("<h1>",key,":",value,"<h2>");
                  ]
                  b=0;
                  Loop(f.1)Condition(true):[
                    Print("<h1>",value,"<h1>");
                    f.1=(f.1)+1;
                    If f.1 == 101:[Return 1;]
                  ]
                  Print("<a href='debug.q'>Goto Debug.q</a>");

                .q>
                </ul>
            </div>

        </div>
        {{BOOTSTRAP.js_bundle_min}}

        <table border="3px">
        <q.
          Loop(data):[
            Print("<tr>",Line,Space(8));
            Loop(value):[
               Print("<td>",value,"</td>",Line,Space(8));
            ]
            Print("</tr>",Line,Space(8));
          ]
        .q>
        </table>
    </body>
</html>