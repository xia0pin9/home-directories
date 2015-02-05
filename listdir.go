package main

import (
    "fmt"
    "flag"
    "os"
    "io/ioutil"
)

func usage() {
    fmt.Fprintf(os.Stderr, "usage: %s [inputdir]\n", os.Args[0])
    flag.PrintDefaults()
    //os.Exit(1)
}

func main() {
    flag.Usage = usage
    flag.Parse()

    args := flag.Args()
    if len(args) < 1 {
        fmt.Println("Input directory is missing")
        os.Exit(1)
    }
    files, _ := ioutil.ReadDir(os.Args[1])
    for _, f := range files {
        fmt.Println(f.Name())
    }
}
