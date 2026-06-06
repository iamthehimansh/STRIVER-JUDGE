import json

INPUT = "/Users/iamthehimansh/Downloads/stiver'sdata/striver_a2z.json"
OUTPUT = "/Users/iamthehimansh/Downloads/stiver'sdata/browser_scraper.js"


with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)


problems = []

for cat in data:
    for sub in cat["subcategories"]:
        for p in sub["problems"]:

            if not p.get("plus"):
                continue

            problems.append({
                "category_id": cat["category_id"],
                "category_name": cat["category_name"],
                "subcategory_id": sub["subcategory_id"],
                "subcategory_name": sub["subcategory_name"],
                **p,
                "slug": p["plus"].split("/")[-1]
            })


browser_js = """
(async()=>{

console.clear();

const problems = __DATA__;

const BASE =
"https://backend-go.takeuforward.org/api/v2/plus/problem/";

let output = [];
let failed = [];


console.log(
"TOTAL:",
problems.length
);


for(
 let i=0;
 i<problems.length;
 i++
){

 const item = problems[i];

 console.log(
   i+1,
   "/",
   problems.length,
   item.slug
 );


 try{

   const res = await fetch(
      BASE+
      item.slug+
      "?subjectSlug=dsa"
   );


   const json =
      await res.json();


   output.push({

      meta:item,

      details:json.data

   });


 }
 catch(e){

   failed.push(item);

 }


 await new Promise(
   r=>setTimeout(r,50)
 );

}


const finalJSON = {

 total:output.length,

 failed:failed,

 problems:output

};



const blob =
new Blob(
[
 JSON.stringify(
   finalJSON,
   null,
   2
 )
],
{
 type:"application/json"
}
);



const a =
document.createElement("a");


a.href =
URL.createObjectURL(blob);


a.download =
"FULL_STRIVER_DATABASE.json";


a.click();


console.log(
"DONE",
finalJSON
);


})();
"""


browser_js = browser_js.replace(
    "__DATA__",
    json.dumps(problems)
)


with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as f:
    f.write(browser_js)


print("Created:")
print(OUTPUT)

print("Problems:")
print(len(problems))