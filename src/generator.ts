import * as path from "path";

import { listAllFiles, copyAndReplace } from "./utils";
import { Template } from "./template";

function resolveTemplateFilePath(template: Template): string {
  return `${path.resolve(__dirname, "../templates", template.name)}`;
}

function renameRelativeFilePath(
  projectName: string,
  template: Template,
  relativeFilePath: string
): string {
  let p = relativeFilePath
    .replace(/HelloWorld/g, projectName)
    .replace(/helloworld/g, projectName.toLowerCase());
  template.dotFiles.forEach(dotfile => {
    p = p.replace(dotfile.templateName, dotfile.realName);
  });
  return p;
}

export default function generateSkygearServer(
  projectName: string,
  template: Template
) {
  const destPath = projectName;
  const srcPath = resolveTemplateFilePath(template);
  const allFilesInTemplate = listAllFiles(srcPath);
  allFilesInTemplate.forEach(absoluteSrcFilePath => {
    const relativeFilePath = path.relative(srcPath, absoluteSrcFilePath);
    const relativeRenamedPath = renameRelativeFilePath(
      projectName,
      template,
      relativeFilePath
    );
    copyAndReplace(
      absoluteSrcFilePath,
      path.resolve(destPath, relativeRenamedPath),
      {
        HelloWorld: projectName,
        helloworld: projectName.toLowerCase(),
      }
    );
  });
}
