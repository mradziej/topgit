#!/bin/sh

color=
do_dfs=false
do_bfs=false
stack=
reverse=
header=
body=

summary_graphviz=--graphviz

name=

while [ -n "$1" ]; do
	arg="$1"; shift
	case "$arg" in
	--color)
		color="color";;
	--no-color)
		color="no-color";;
	--dfs)
		do_dfs=true;;
	--bfs)
		do_bfs=true;;
	--reverse)
		reverse="reverse";;
	--no-reverse)
		reverse="no-reverse";;
	--header)
		header="header";;
	--no-header)
		header="no-header";;
	--body)
		body="body";;
	--no-body)
		body="no-body";;
	-*)
		echo "Usage: tg [...] graph [--color] [--bfs|--dfs] [--reverse] [--header] [--body] [NAME]" >&2
		exit 1;;
	*)
		[ -z "$name" ] ||
			die "branch already specified ($branch)"
		name="$arg";;
	esac
done

[ -z "$name" ] || git rev-parse --verify "$name" 2>/dev/null ||
		die "invalid branch name: $name"

[ -z "$name" ] || name="-X \"$name\""

[ -r "@sharedir@"/graph.gvpr ] || 
	die "Can't find graph.gvpr file in \`@sharedir@'"

[ "$header" = "header" -o "$body" = "body" ] &&
	summary_graphviz=--graphviz=verbose

$do_dfs && $do_bfs &&
	die "--bfs and --dfs options are mutual exclusive"
$do_bfs && stack="no-stack"
$do_dfs && stack="stack"

type ccomps >/dev/null 2>&1 ||
	die "need the ccomps(1) tool from the graphviz package"
type gvpr >/dev/null 2>&1 ||
	die "need the gvpr(1) tool from the graphviz package"

setup_pager

$tg summary $summary_graphviz |
	ccomps -x $name |
	gvpr -a "$color $stack $reverse $header $body" \
	     -f "@sharedir@"/graph.gvpr
