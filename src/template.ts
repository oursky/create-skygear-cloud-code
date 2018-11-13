export interface Template {
  name: string;
  dotFiles: DotFile[];
}

interface DotFile {
  templateName: string;
  realName: string;
}

function makeTemplate(name: string, dotFiles: DotFile[]): Template {
  return {
    name,
    dotFiles,
  };
}

function makeDotFile(templateName: string, realName: string): DotFile {
  return {
    templateName,
    realName,
  };
}

export const PythonTemplate = makeTemplate("HelloWorld", [
  makeDotFile("_gitignore", ".gitignore"),
  makeDotFile("_skyignore", ".skyignore"),
  makeDotFile("_travis.yml", ".travis.yml"),
]);
