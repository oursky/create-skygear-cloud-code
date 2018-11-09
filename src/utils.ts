import * as fs from "fs";
import * as path from "path";

export function listAllFiles(srcPath: string): [string] {
  if (!fs.lstatSync(srcPath).isDirectory()) {
    return [srcPath];
  }

  const files = fs.readdirSync(srcPath).map(childPath => {
    const _childPath = path.join(srcPath, childPath);
    return listAllFiles(_childPath);
  });
  return [].concat.apply([srcPath], files);
}

export function copyAndReplace(
  srcPath: string,
  destPath: string,
  replacements: { [key: string]: string } = {}
) {
  if (fs.lstatSync(srcPath).isDirectory()) {
    if (!fs.existsSync(destPath)) {
      fs.mkdirSync(destPath);
    }
    return;
  }

  const srcPermissions = fs.statSync(srcPath).mode;
  let content = fs.readFileSync(srcPath, "utf8");
  Object.keys(replacements).forEach(regex => {
    content = content.replace(new RegExp(regex, "g"), replacements[regex]);
  });
  fs.writeFileSync(destPath, content, {
    encoding: "utf8",
    mode: srcPermissions,
  });
}
