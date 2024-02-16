from bucket3.hasher import Hasher


class TestHasher:
    filename = 'foo.png'
    checksum = 'YDijXrI5xhQmdRP9Kp7QTHWm+wxUP9Xo22KLJqAv/WA='
    key = 'YDijXrI5xhQmdRP9Kp7QTHWm-wxUP9Xo22KLJqAv_WA.png'

    def test_key_to_checksum(self):
        hasher = Hasher.from_key(self.key)
        assert hasher.checksum() == self.checksum

    def test_checksum_to_key(self):
        hasher = Hasher.from_checksum(self.checksum, self.filename)
        assert hasher.key() == self.key
        assert str(hasher) == self.key
