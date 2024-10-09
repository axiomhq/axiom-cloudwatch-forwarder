{
  description = "A Nix wrapperd python development environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/24.05";
    nixpkgsUnstable.url = "github:nixos/nixpkgs/nixos-unstable";
    flakeUtils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, nixpkgsUnstable, flakeUtils, ... }:
    flakeUtils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pkgsUnstable = nixpkgsUnstable.legacyPackages.${system};
      in
      {
        devShell = pkgs.mkShell
          {
            packages = with pkgs;
              [
                python39
              ] ++ (with pkgsUnstable; [
                uv
              ]);
          };
      });
}
