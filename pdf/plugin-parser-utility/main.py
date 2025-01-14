import base64
import json
import numpy as np
import sys
import typer

def main(workbench_api_url: str, json_arguments: str, output_html: str):

    # Load parameters
    dec_args = json.loads(json_arguments)

    # Compute sparse features
    file_to_idx = {}
    ft_to_idx = {}
    file_ft = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        obj = json.loads(line)
        file_name = obj.pop('_id')
        file_idx = len(file_to_idx)
        file_to_idx[file_name] = file_idx

        for k, v in obj.items():
            if k.startswith('ml-test') or k.startswith('plugin-rl-grit'):
                # Filter out these for now... need to change to user-specified
                # filter.
                continue

            ft_idx = ft_to_idx.get(k)
            if ft_idx is None:
                ft_idx = len(ft_to_idx)
                ft_to_idx[k] = ft_idx

            file_ft.append((file_idx, ft_idx))

    X = np.zeros((len(file_to_idx), len(ft_to_idx)))
    X_nonzero = np.asarray(file_ft, dtype=int)
    X[X_nonzero[:, 0], X_nonzero[:, 1]] = 1.

    # X is (file, ft) at the moment. We actually want to find features which
    # are the same.
    X = X.T
    label_counts = X.sum(1)

    # And we want each dim to be zero mean, unit std s.t. euclidean distance
    # takes rarity into account.
    X -= X.mean(1, keepdims=True)
    X /= X.std(1, keepdims=True) + 1e-30

    labels = [None for _ in range(len(ft_to_idx))]
    for k, v in ft_to_idx.items():
        labels[v] = k

    if False:
        # This is slow! Limit to first 100 files...
        X = X[:50, :50]
        labels = labels[:50]
        label_counts = label_counts[:50]

    with open(output_html, 'w') as f:
        f.write('<!DOCTYPE html>\n<html>')
        f.write('<head><title>FAW Parser Utility plugin</title>')
        f.write(r'''<style lang="text/css">
                </style>''')
        f.write('</head>')
        f.write('<body>')
        f.write(parser_classes(labels, X))
        f.write('</body>')
        f.write('</html>')


def parser_classes(labels, X):
    """Returns an HTML table describing the mutual information amongst parsers.
    """
    import scipy.optimize

    parsers = {}
    for li, l in enumerate(labels):
        p = l.split('_')[0]
        plist = parsers.get(p)
        if plist is None:
            parsers[p] = plist = []
        plist.append(li)

    all_parsers = sorted(parsers.items(), key=lambda m: len(m[1]))

    # Want to know cos(theta), Ax * B / (||Ax|| ||B||)

    matrix = []
    for pi, (p, plist) in enumerate(all_parsers):
        prow = []
        matrix.append(prow)

        # Try to predict the parser under investigation's features from this
        # parser's features
        for ji, (j, jlist) in enumerate(all_parsers[:pi+1]):
            mat_p = X[np.asarray(jlist)].T
            if ji == pi:
                prow.append(mat_p.shape[1])

                # Finally, look at ALL preceding parsers
                jlist_all = [v for l in all_parsers[:pi] for v in l[1]]
                if not jlist_all:
                    assert ji == pi
                    prow.insert(0, mat_p.shape[1])
                    continue
                mat_p = X[np.asarray(jlist_all)].T

            pvals = []
            for jj in plist:
                # Compute multiple correlation from mat_p to X[jj]
                # Note that we already zero-meaned and unit-var'd everything

                if X[jj].std() == 0.:
                    # Perfectly useless feature
                    pvals.append(0.)
                    continue

                R = mat_p.T @ mat_p / mat_p.shape[0]
                c = mat_p.T @ X[jj, None].T / mat_p.shape[0]

                # Pseudo-inverse accounts for when dependent variables are
                # somewhat fully determined by one another
                R_inv = np.linalg.pinv(R)

                r_sqr = (c.T @ R_inv @ c)[0, 0]
                assert r_sqr >= -1e3 and r_sqr <= 1.1, r_sqr
                pvals.append(1 - r_sqr ** 0.5)

            if ji != pi:
                prow.append(np.asarray(pvals).sum())
            else:
                prow.insert(0, np.asarray(pvals).sum())

        prow.extend([None for _ in range(pi+1, len(all_parsers))])

    r = []
    r.append('<div>Parser utility; values are useful features row adds against column, measured as sum across all features of 1 - R from Pearson multiple correlation.</div>')
    r.append('<div>Diagonal is number of features from parser.</div>')
    r.append('<div>"Novel features" column indicates number of useful features added to dataset compared to previous rows.</div>')
    r.append('<table border="1"><tr><td></td><td>Novel features</td>')
    for p, _ in all_parsers:
        r.append(f'<td>{p}</td>')
    r.append('</tr>')
    novel_sum = 0.
    all_sum = 0.
    for pi, ((p, _), mrow) in enumerate(zip(all_parsers, matrix)):
        r.append(f'<tr><td>{p}</td>')

        novel_sum += mrow[0]
        all_sum += mrow[pi + 1]

        for v in mrow:
            if v is None:
                r.append('<td></td>')
            else:
                r.append(f'<td>{v:.3f}</td>')
        r.append('</tr>')
    r.append(f'<tr><td>Approximate novel features</td><td>{novel_sum:.3f}</td></tr>')
    r.append(f'<tr><td>Out of</td><td>{all_sum:.3f}</td></tr>')
    r.append('</table>')
    return ''.join(r)


if __name__ == '__main__':
    typer.run(main)

