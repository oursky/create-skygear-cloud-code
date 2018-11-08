import * as program from "commander";

program.version("1.0.0").description("Scaffolding for skygear server");

program.on("command:*", () => {
  console.error("Invalid command: %s", program.args.join(" "));
  program.help();
});

program.parse(process.argv);
if (process.argv.slice(2).length === 0) {
  console.error(
    "You didn't pass any command\nSee --help for a list of available commands."
  );
}
