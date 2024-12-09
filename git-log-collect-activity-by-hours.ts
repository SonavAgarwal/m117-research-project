/* cat data-collection/malicious/jia-xz-commits.txt | bun run git-log-collect-activity-by-hours.ts > jia-xz-commits.txt.activity.csv */

const re = /(\d+):(\d+):(\d+)/gm;
let str = new String();
for await (const line of console) {
  str += line + "\n";
}

const hours = new Array(24).fill(0);
for (const match of str.matchAll(re)) {
  const hour = parseInt(match[1]);

  hours[hour] += 1;
}

console.log("local_hours,count");
for (let i = 0; i < 24; i++) {
  console.log(`${i.toString().padStart(2, "0")},${hours[i]}`);
}
