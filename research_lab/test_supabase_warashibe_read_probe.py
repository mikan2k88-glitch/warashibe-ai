from research_lab.supabase_warashibe_read_probe import probe


def main():
    result = probe(environ={})
    assert result['status'] == 'not_configured'
    assert result['read_ok'] is False
    assert result['tables'] == {}
    print('Offline read probe tests passed')


if __name__ == '__main__':
    main()
