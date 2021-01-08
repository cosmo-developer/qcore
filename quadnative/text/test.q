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
                  Loop(b)Condition(true):[
                    Print("<h1>",value,"<h1>");
                    b=b+1;
                    If b == 101:[Return 1;]
                  ]
                  Print("<a href='debug.q'>Goto Debug.q</a>");
Python[[
print("something");
def something():
    return "myname"

print(something())
]]
                .q>
                </ul>
            </div>

        </div>
        {{BOOTSTRAP.js_bundle_min}}
        <h2>{{f}}<br>{{d}}</h2>
        <table border="3px">
        <q.
          Include(`example.q`);
          Loop(data):[
            Print("<tr>",Line,Space(8));
            Loop(value):[
               Print("<td>",value,"</td>",Line,Space(8));
            ]
            Print("</tr>",Line,Space(8));
          ]
          var="str";
          var.Add("USA");
          Print(var);
          LANGUAGE.version=2;
          Print("some");
          LANGUAGE.lbs.name="something";
          Print(LANGUAGE.version,LANGUAGE.lbs.name.ES);
          Print("murga".EN);
          Print(Line,LANGUAGE);
          Print(Line,ARRAYDATA,Line);
          Print(ARRAYDATA.Length);
          Print(ARRAYDATA.array.name.Length);
          Print(ARRAYDATA);
          ARRAYDATA.array.Delete("name");
          Print(Line,ARRAYDATA.array);
          a=(5,4,8,7,5,4,7,8);
          a.Delete(1);
          Print(Line,a," With:",a.Length,Line);
          d="Delegete";
          d.Add("uri")at(1);
          Print(Line,d,Line);
          arra=(5,6,7,8,8,9);
          arra.Add(44)at(3);
          Print(arra,Line);
          Print(LANGUAGE,Line);
          LANGUAGE.lbs.name.Add("horror")at(2);
          Print(LANGUAGE,Line);
          LANGUAGE.array=(5,8,7,8,8);
          LANGUAGE.array.Add(888)at(2);
          Print(LANGUAGE,Line);
          MyFunc(some,aux):[
             Return some&aux;
          ];
          Print(MyFunc(LANGUAGE.lbs.name,"Don"));
        .q>
        </table>
    </body>
</html>