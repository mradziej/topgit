#!/usr/bin/python

import git

def topo_sort(start, next_fn, done):
    if done is None:
        done = set()
    result = []
    for name in start:
        if name not in done:
            result += topo_sort(next_fn(name), next_fn, done)
            result.append(name)
            done.add(name)
    return result

class TopGit(object):
    def __init__(self, repo):
        self.repo = repo
        self.bases = dict(
            (h.name, h)
            for h in Heads.list_from_string(
                repo,
                repo.git.for_each_ref("refs/top-bases", format="%(refname)%00%(objectname)"))
        self.topics = dict((head.name, self.bases["refs/top-bases/%s" % head.name]),
                           for head in repo.heads 
                           if '.topdeps' in head.commit.tree)
     
     def branch(self, name):
        return self.topics[name]
     
     def precessors(self, name):
         return topo_sort(self, [name], lambda b: self.get_branch(b).deps())
     
     def successors(self, name):
         return topo_sort(self, [name], lambda b: self.children(b))
     
     def children(self, name):
         children = getattr(self, '_children')
         if children is None:
             children = {}
             for branch in self.topics.itervalues():
                 for dep in branch.deps():
                    children.setdefault(dep, []).append(branch.name)
             self.children = children
         return children[name]
                 
    def topics_by_path(self, path):
        by_branch = getattr(self, '_topics_by_branch')
        if by_branch is None:
            by_branch = {}
            

class TopBranch(object):
    def __init__(self, repo, base, head):
        self.base = base
        self.head = head
        # self.head =  [h for h in repo.heads if h.name=='master'][0]
        
    def message(self):
        return self.head.commit.tree['.topmsg'].data
    
    def deps(self):
        """Returns the names of the branches on which this one depends."""
        deps = getattr(self, '_deps')
        if deps is None:
            deps = [name for name in self.commit.tree['.topdeps'].data. split()]
        return deps

    def patch(self, repo):
        return repo.diff(self.base.commit, self.head.commit)

        