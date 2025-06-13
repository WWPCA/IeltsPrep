{pkgs}: {
  deps = [
    pkgs.aws-sam-cli
    pkgs.ffmpeg-full
    pkgs.postgresql
    pkgs.openssl
  ];
}
