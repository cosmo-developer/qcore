<html>
<head>
<title>{{SITE.home_title}}</title>
{{BOOTSTRAP.css_bundle_min}}
</head>
<body>
<q.
  Include(`example.q`);
  var = (name="Sonu",from="India");
  Print(var("My name is {name} from {from}"),Line);
  List(var);
  Print(name,Space,from,Line);
  Print(Type(var),Line);
  time="2018/01/25 11:22:59";
  time.Time("Y/m/d H:M:S")to("Y-m-d H:M:S")plus(7 days);
  Print(time,Line);
  value=8888.999999;
  Print(Type(value),Line);
  Print(value.Num("00000.0000"),Line);
  Id(2);
  Print(DB.self,Line);
  Jump(2)Times(5);
  str="sod";
  str.Add("kernel")at(2);
  Print(str);
.q>
{{BOOTSTRAP.array_data.user.Replace("H")With("h")}}
{{DOES.some(`r`-"r")limits(4)}}
{{LANGUAGE.lbs.some.Find("o")}}
{{LANGUAGE.lbs.some.Length}}
{{DB.self}}
{{Login(DB.username,DB.password)}}
</body>
</html>