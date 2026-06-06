import json

INPUT="/Users/iamthehimansh/Downloads/stiver'sdata/striver_a2z.json"

OUTPUT="/Users/iamthehimansh/Downloads/stiver'sdata/browser_scraper.js"


with open(INPUT) as f:
    data=json.load(f)


items=[]

seen=set()


for cat in data:
    for sub in cat["subcategories"]:
        for p in sub["problems"]:

            plus=p.get("plus")

            if not plus:
                continue

            slug=plus.split("/")[-1]

            items.append({
                **p,

                "slug":slug,

                "category":
                    cat["category_name"],

                "subcategory":
                    sub["subcategory_name"]
            })


print(
    "ROWS:",
    len(items)
)


unique={}

for x in items:
    unique[x["slug"]]=x


print(
    "UNIQUE:",
    len(unique)
)



js=f"""

(async()=>{{

const problems =
{json.dumps(list(unique.values()))};


const BASE =
"https://backend-go.takeuforward.org/api/v2/plus/problem/";


let done=[];
let failed=[];


console.log(
"START",
problems.length
);



for(
 let i=0;i<problems.length;i++
){{

let p=problems[i];


console.log(
i+1,
"/",
problems.length,
p.slug
);



try{{

let res=await fetch(
BASE+p.slug+"?subjectSlug=dsa"
);


if(!res.ok){{

throw new Error(
"HTTP "+res.status
);

}}


let json=
await res.json();


if(
 !json.success ||
 !json.data
){{

throw new Error(
"bad json"
);

}}



done.push({{

meta:p,

problem:json.data

}});


}}
catch(e){{


console.error(
"FAILED",
p.slug,
e.message
);


failed.push({{

slug:p.slug,

name:p.problem_name,

error:e.message

}});


}}


await new Promise(
r=>setTimeout(r,80)
);

}}



let result={{

success:done.length,

failed_count:
failed.length,

failed,

problems:done

}};



let a=document.createElement("a");


a.href=
URL.createObjectURL(
new Blob(
[
JSON.stringify(
result,
null,
2
)
],
{{type:"application/json"}}
)
);


a.download=
"STRIVER_FULL_FINAL.json";


a.click();



console.table(failed);

console.log(result);


}})();

"""


open(
OUTPUT,
"w"
).write(js)


print(
"generated",
OUTPUT
)